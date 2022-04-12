# -*- coding: utf-8 -*-

import pathlib
import shutil
from datetime import datetime

from zimscraperlib.image.transformation import resize_image

from .constants import ROOT_DIR, Conf
from .scraper_category import ScraperCategory
from .scraper_guide import ScraperGuide
from .scraper_homepage import ScraperHomepage
from .scraper_info import ScraperInfo
from .shared import Global, GlobalMixin, logger
from .utils import setup_s3_and_check_credentials


class ifixit2zim(GlobalMixin):
    def __init__(self, **kwargs):

        Global.conf = Conf(**kwargs)
        for option in Global.conf.required:
            if getattr(Global.conf, option) is None:
                raise ValueError(f"Missing parameter `{option}`")

        add_item_methods = {
            "guide": self._add_guide_to_scrape,
            "category": self._add_category_to_scrape,
            "home": self._add_home_to_scrape,
            "info": self._add_info_to_scrape,
        }
        self.scraper_homepage = ScraperHomepage(add_item_methods=add_item_methods)
        self.scraper_guide = ScraperGuide(add_item_methods=add_item_methods)
        self.scraper_category = ScraperCategory(add_item_methods=add_item_methods)
        self.scraper_info = ScraperInfo(add_item_methods=add_item_methods)
        self.scrapers = [
            self.scraper_homepage,
            self.scraper_category,
            self.scraper_guide,
            self.scraper_info,
        ]

    def _add_guide_to_scrape(self, guide_id, locale):
        self.scraper_guide.add_item_to_scrape(
            guide_id,
            {
                "guideid": guide_id,
                "locale": locale,
            },
        )

    def _add_category_to_scrape(self, category_id):
        self.scraper_category.add_item_to_scrape(
            category_id,
            {
                "categoryid": category_id,
            },
        )

    def _add_info_to_scrape(self, info_title, info_data):
        self.scraper_info.add_item_to_scrape(info_title, info_data)

    def _add_home_to_scrape(self):
        self.scraper_homepage.add_item_to_scrape(1, 1)  # Dummy item

    @property
    def build_dir(self):
        return self.conf.build_dir

    def cleanup(self):
        """Remove temp files and release resources before exiting"""
        if not self.conf.keep_build_dir:
            logger.debug(f"Removing {self.build_dir}")
            shutil.rmtree(self.build_dir, ignore_errors=True)

    def sanitize_inputs(self):
        """input & metadata sanitation"""
        logger.debug("Checking user-provided metadata")

        if not self.conf.name:
            self.conf.name = "ifixit_{lang}_{selection}".format(
                lang=self.conf.language["iso-639-1"],
                selection="selection" if self.conf.categories else "all",
            )

        period = datetime.now().strftime("%Y-%m")
        if self.conf.fname:
            # make sure we were given a filename and not a path
            self.conf.fname = pathlib.Path(self.conf.fname.format(period=period))
            if pathlib.Path(self.conf.fname.name) != self.conf.fname:
                raise ValueError(f"filename is not a filename: {self.conf.fname}")
        else:
            self.conf.fname = f"{self.conf.name}_{period}.zim"

        if not self.conf.title:
            self.conf.title = self.metadata["title"]
        self.conf.title = self.conf.title.strip()

        if not self.conf.description:
            self.conf.description = self.metadata["description"]
        self.conf.description = self.conf.description.strip()

        if not self.conf.author:
            self.conf.author = "iFixit"
        self.conf.author = self.conf.author.strip()

        if not self.conf.publisher:
            self.conf.publisher = "openZIM"
        self.conf.publisher = self.conf.publisher.strip()

        self.conf.tags = list(
            set(
                self.conf.tag
                + ["_category:iFixit", "iFixit", "_videos:yes", "_pictures:yes"]
            )
        )

        logger.debug(
            "Configuration after sanitization:\n"
            f"name: {self.conf.name}\n"
            f"fname: {self.conf.fname}\n"
            f"name: {self.conf.author}\n"
            f"fname: {self.conf.publisher}"
        )

    def add_assets(self):
        """download and add site-wide assets, identified in metadata step"""
        logger.info("Adding assets")

        # recursively add our assets, at a path identical to position in repo
        assets_root = pathlib.Path(ROOT_DIR.joinpath("assets"))
        for fpath in assets_root.glob("**/*"):
            if not fpath.is_file():
                continue
            path = str(fpath.relative_to(ROOT_DIR))

            logger.debug(f"> {path}")
            with self.lock:
                self.creator.add_item_for(path=path, fpath=fpath)

    def add_illustrations(self):
        logger.info("Adding illustrations")

        src_illus_fpath = pathlib.Path(ROOT_DIR.joinpath("assets", "illustration.png"))
        tmp_illus_fpath = pathlib.Path(self.build_dir, "illustration.png")

        shutil.copy(src_illus_fpath, tmp_illus_fpath)

        # resize to appropriate size (ZIM uses 48x48 so we double for retina)
        for size in (96, 48):
            resize_image(tmp_illus_fpath, width=size, height=size, method="thumbnail")
            with open(tmp_illus_fpath, "rb") as fh:
                with self.lock:
                    self.creator.add_illustration(size, fh.read())

    def run(self):
        s3_storage = (
            setup_s3_and_check_credentials(self.conf.s3_url_with_credentials)
            if self.conf.s3_url_with_credentials
            else None
        )
        s3_msg = (
            f"\n"
            f"  using cache: {s3_storage.url.netloc} "
            f"with bucket: {s3_storage.bucket_name}"
            if s3_storage
            else ""
        )
        del s3_storage

        logger.info(
            f"Starting scraper with:\n"
            f"  language: {self.conf.language['english']}"
            f" ({self.conf.domain})\n"
            f"  output_dir: {self.conf.output_dir}\n"
            f"  build_dir: {self.build_dir}\n"
            f"{s3_msg}"
        )

        Global.metadata = self.scraper_homepage.get_online_metadata()
        logger.debug(
            f"Additional metadata scrapped online:\n"
            f"title: {self.metadata['title']}\n"
            f"description: {self.metadata['description']}\n"
            f"footer_stats: {self.metadata['footer_stats']}\n"
            f"footer_copyright: {self.metadata['footer_copyright']}\n"
        )
        self.sanitize_inputs()

        logger.debug("Starting Zim creation")
        Global.setup()
        self.creator.start()

        for scraper in self.scrapers:
            scraper.setup()

        try:

            self.add_assets()
            self.add_illustrations()

            for scraper in self.scrapers:
                scraper.build_expected_items()

            for scraper in self.scrapers:
                scraper.scrape_items()

            logger.info("Awaiting images")
            Global.img_executor.shutdown()

            stats = "Stats: "
            for scraper in self.scrapers:
                stats += f"{len(scraper.expected_items)} {scraper.get_items_name()}, "
            for scraper in self.scrapers:
                stats += (
                    f"{len(scraper.missing_items)} missing {scraper.get_items_name()}, "
                )
            for scraper in self.scrapers:
                stats += (
                    f"{len(scraper.missing_items)} {scraper.get_items_name()}"
                    " in error, "
                )
            stats += f"{self.imager.nb_requested} images"

            logger.info(stats)

        except Exception as exc:
            # request Creator not to create a ZIM file on finish
            self.creator.can_finish = False
            if isinstance(exc, KeyboardInterrupt):
                logger.error("KeyboardInterrupt, exiting.")
            else:
                logger.error(f"Interrupting process due to error: {exc}")
                logger.exception(exc)
            self.imager.abort()
            Global.img_executor.shutdown(wait=False)
            return 1
        else:
            logger.info("Finishing ZIM file")
            # we need to release libzim's resources.
            # currently does nothing but crash if can_finish=False
            # but that's awaiting impl. at libkiwix level
            with self.lock:
                self.creator.finish()
            logger.info(
                f"Finished Zim {self.creator.filename.name} "
                f"in {self.creator.filename.parent}"
            )
        finally:
            self.cleanup()
