# -*- coding: utf-8 -*-

import pathlib
import tempfile
import urllib.parse
from dataclasses import dataclass, field
from typing import List, Optional, Set

from zimscraperlib.i18n import get_language_details

ROOT_DIR = pathlib.Path(__file__).parent
NAME = ROOT_DIR.name
DEFAULT_HOMEPAGE = "Main-Page"

with open(ROOT_DIR.joinpath("VERSION"), "r") as fh:
    VERSION = fh.read().strip()

SCRAPER = f"{NAME} {VERSION}"

IMAGES_ENCODER_VERSION = 1
URLS = {
    "en": "https://www.ifixit.com",
    "fr": "https://fr.ifixit.com",
    "pt": "https://pt.ifixit.com",
}

DEFAULT_GUIDE_IMAGE_URL = (
    "https://assets.cdn.ifixit.com/static/images/"
    "default_images/GuideNoImage_300x225.jpg"
)

DEFAULT_DEVICE_IMAGE_URL = (
    "https://assets.cdn.ifixit.com/static/images/"
    "default_images/DeviceNoImage_300x225.jpg"
)

DEFAULT_WIKI_IMAGE_URL = (
    "https://assets.cdn.ifixit.com/static/images/"
    "default_images/WikiNoImage_300x225.jpg"
)

# Open this URL in the various languages to retrieve labels below
# https://www.ifixit.com/api/2.0/guides?guideids=219,220,202,206,46465
DIFFICULTY_VERY_EASY = [
    "Very easy",
    "Muito fácil",
    "Très facile",
    "Sehr einfach",
    "Muy fácil",
    "Molto facile",
    "Çok kolay",
    "とても簡単",
    "Zeer eenvoudig",
    "Очень просто",
    "아주 쉬움",
    "非常容易",
]  # guide 219
DIFFICULTY_EASY = [
    "Easy",
    "Fácil",
    "Facile",
    "Einfach",
    "Fácil",
    "Facile",
    "Kolay",
    "簡単",
    "Eenvoudig",
    "Просто",
    "쉬움",
    "简单",
]  # guide 220
DIFFICULTY_MODERATE = [
    "Moderate",
    "Moderado",
    "Modérée",
    "Mittel",
    "Moderado",
    "Moderato",
    "Orta",
    "普通",
    "Gemiddeld",
    "Средняя",
    "보통",
    "中等",
]  # guide 202
DIFFICULTY_HARD = [
    "Difficult",
    "Difícil",
    "Difficile",
    "Schwierig",
    "Difícil",
    "Difficile",
    "Zor",
    "難しい",
    "Moeilijk",
    "Сложно",
    "어려움",
    "困难",
]  # guide 206
DIFFICULTY_VERY_HARD = [
    "Very difficult",
    "Muito difícil",
    "Très difficile",
    "Sehr schwierig",
    "Muy difícil",
    "Molto difficile",
    "Çok zor",
    "とても難しい",
    "Zeer moeilijk",
    "Очень сложно",
    "매우 어려움",
    "非常困难",
]  # guide 46465

# Browse these pages in the various languages to retrieve category + guide labels
# https://www.ifixit.com/Device/Mac
# https://www.ifixit.com/Device/Apple_Watch
# https://www.ifixit.com/Device/Logitech__G502_Hero
# https://www.ifixit.com/Guide/MacBook+Air+11-Inch+Late+2010+Battery+Replacement/4384
# https://www.ifixit.com/Teardown/Apple+Watch+Teardown/40655

CATEGORY_LABELS = {
    "en": {
        "author": "Author: ",
        "categories": " Categories",
        "featured_guides": "Featured Guides",
        "technique_guides": "Techniques",
        "replacement_guides": "Replacement Guides",
        "teardown_guides": "Teardowns",
        "related_pages": "Related Pages",
        "in_progress_guides": "In Progress Guides",
        "disassembly_guides": "Disassembly Guides",
        "repairability": "Repairability:",
    },
    "fr": {
        "author": "Auteur: ",
        "categories": " catégories",
        "featured_guides": "Tutoriels vedettes",
        "technique_guides": "Techniques",
        "replacement_guides": "Tutoriels de remplacement",
        "teardown_guides": "Vues éclatées",
        "related_pages": "Pages connexes",
        "in_progress_guides": "Tutoriels en cours",
        "disassembly_guides": "Tutoriels de démontage",
        "repairability": "Réparabilité:",
    },
    "pt": {
        "author": "Autor: ",
        "categories": " categorias",
        "featured_guides": "Guia em destaque",
        "technique_guides": "Técnicas",
        "replacement_guides": "Guias de reposição",
        "teardown_guides": "Teardowns",
        "related_pages": "Páginas relacionadas",
        "in_progress_guides": "Guias em andamento",
        "disassembly_guides": "Guias de Desmontagem",
        "repairability": "Reparabilidade:",
    },
}

GUIDE_LABELS = {
    "en": {
        "written_by": "Written By:",
        "difficulty": "Difficulty",
        "steps": "Steps",
        "time_required": " Time Required",
        "sections": "Sections",
        "flags": "Flags",
        "introduction": "Introduction",
        "step_no": "Step ",
        "conclusion": "Conclusion",
        "author": "Author",
        "reputation": "Reputation",
        "member_since": "Member since: ",
        "published": "Published: ",
        "teardown": "Teardown",
    },
    "fr": {
        "written_by": "Rédigé par :",
        "difficulty": "Difficulté",
        "steps": "Étapes",
        "time_required": "Temps nécessaire",
        "sections": "Sections",
        "flags": "Drapeaux",
        "introduction": "Introduction",
        "step_no": "Étape ",
        "conclusion": "Conclusion",
        "author": "Auteur",
        "reputation": "Réputation",
        "member_since": "Membre depuis le ",
        "published": "Publication : ",
        "teardown": "Vue éclatée",
    },
    "pt": {
        "written_by": "Escrito Por:",
        "difficulty": "Dificuldade",
        "steps": "Passos",
        "time_required": "Tempo necessário",
        "sections": "Partes",
        "flags": "Sinalizadores",
        "introduction": "Introdução",
        "step_no": "Passo ",
        "conclusion": "Conclusão",
        "author": "Autor(a)",
        "reputation": "Reputação",
        "member_since": "Membro desde: ",
        "published": "Publicado em: ",
        "teardown": "Teardown",
    },
}


API_PREFIX = "/api/2.0"


@dataclass
class Conf:
    required = [
        "lang_code",
        "output_dir",
    ]

    lang_code: str = ""
    language: dict = field(default_factory=dict)
    main_url: str = ""

    # zim params
    name: str = ""
    title: Optional[str] = ""
    description: Optional[str] = ""
    author: Optional[str] = ""
    publisher: Optional[str] = ""
    fname: Optional[str] = ""
    tag: List[str] = field(default_factory=list)

    # customization
    icon: Optional[str] = ""
    categories: Set[str] = field(default_factory=set)
    categories_include_children: Optional[bool] = False

    # filesystem
    _output_dir: Optional[str] = "."
    _tmp_dir: Optional[str] = "."
    output_dir: Optional[pathlib.Path] = None
    tmp_dir: Optional[pathlib.Path] = None

    # performances
    nb_threads: Optional[int] = -1
    s3_url_with_credentials: Optional[str] = ""

    # error handling
    max_missing_guides: Optional[int] = 0
    max_missing_categories: Optional[int] = 0
    max_missing_info_wikis: Optional[int] = 0
    max_error_guides: Optional[int] = 0
    max_error_categories: Optional[int] = 0
    max_error_info_wikis: Optional[int] = 0

    # debug/devel
    build_dir_is_tmp_dir: Optional[bool] = False
    keep_build_dir: Optional[bool] = False
    debug: Optional[bool] = False
    delay: Optional[float] = 0
    api_delay: Optional[float] = 0
    cdn_delay: Optional[float] = 0
    stats_filename: Optional[str] = None
    skip_checks: Optional[bool] = False

    @staticmethod
    def get_url(lang_code: str) -> urllib.parse.ParseResult:
        return urllib.parse.urlparse(URLS[lang_code])

    @property
    def domain(self) -> str:
        return self.main_url.netloc

    @property
    def api_url(self) -> str:
        return self.main_url + API_PREFIX

    @property
    def s3_url(self) -> str:
        return self.s3_url_with_credentials

    def __post_init__(self):
        self.main_url = Conf.get_url(self.lang_code)
        self.language = get_language_details(self.lang_code)
        self.output_dir = pathlib.Path(self._output_dir).expanduser().resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.tmp_dir = pathlib.Path(self._tmp_dir).expanduser().resolve()
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        if self.build_dir_is_tmp_dir:
            self.build_dir = self.tmp_dir
        else:
            self.build_dir = pathlib.Path(
                tempfile.mkdtemp(prefix=f"ifixit_{self.lang_code}_", dir=self.tmp_dir)
            )

        if self.stats_filename:
            self.stats_filename = pathlib.Path(self.stats_filename).expanduser()
            self.stats_filename.parent.mkdir(parents=True, exist_ok=True)

        # support semi-colon separated tags as well
        if self.tag:
            for tag in self.tag.copy():
                if ";" in tag:
                    self.tag += [p.strip() for p in tag.split(";")]
                    self.tag.remove(tag)

        self.categories = set() if self.categories is None else self.categories
