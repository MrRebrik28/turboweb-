"""Генератор блога local-web.ru и валидной RSS-ленты для Яндекс Дзена.

Создаёт:
1. Карточки-иллюстрации в blog/images/ (копирует из vk_agent/assets/).
2. Страницы статей blog/<slug>.html и индексную страницу blog/index.html.
3. RSS-ленту dzen-rss.xml в корне сайта (https://local-web.ru/dzen-rss.xml).
4. Обновлённый sitemap.xml с учётом всех страниц блога.
"""

from __future__ import annotations

import argparse
import html
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

from blog.articles import ARTICLES

ROOT_DIR = Path(__file__).resolve().parent
SITE_URL = "https://local-web.ru"
ASSETS_SRC_DIR = ROOT_DIR / "vk_agent" / "assets"
BLOG_DIR = ROOT_DIR / "blog"
BLOG_IMAGES_DIR = BLOG_DIR / "images"
RSS_PATH = ROOT_DIR / "dzen-rss.xml"
SITEMAP_PATH = ROOT_DIR / "sitemap.xml"

MSK_TZ = timezone(timedelta(hours=3))


def _sync_images() -> dict[str, int]:
    """Копирует используемые PNG-иллюстрации в blog/images/ и возвращает их размер в байтах."""
    BLOG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    sizes: dict[str, int] = {}
    for article in ARTICLES:
        img_name = article["image"]
        src = ASSETS_SRC_DIR / img_name
        if not src.exists():
            raise FileNotFoundError(f"Не найдено изображение {src} для статьи {article['slug']}")
        dst = BLOG_IMAGES_DIR / img_name
        shutil.copy2(src, dst)
        sizes[img_name] = dst.stat().st_size
    return sizes


def _render_sections_html(sections: list[dict], for_rss: bool = False) -> str:
    """Рендерит блоки статьи в чистый HTML для сайта или <content:encoded> Дзена."""
    chunks: list[str] = []
    for sec in sections:
        sec_type = sec["type"]
        if sec_type == "p":
            cls = "" if for_rss else ' class="text-slate-700 leading-relaxed mb-5 text-base sm:text-lg"'
            chunks.append(f"<p{cls}>{sec['text']}</p>")
        elif sec_type == "h2":
            cls = "" if for_rss else ' class="text-2xl font-black text-[#0F172A] mt-9 mb-4 tracking-tight"'
            chunks.append(f"<h2{cls}>{html.escape(sec['text'])}</h2>")
        elif sec_type in ("ul", "ol"):
            cls = "" if for_rss else (
                ' class="list-disc pl-6 space-y-2.5 text-slate-700 mb-6 text-base sm:text-lg"'
                if sec_type == "ul"
                else ' class="list-decimal pl-6 space-y-2.5 text-slate-700 mb-6 text-base sm:text-lg"'
            )
            li_html = "\n".join(f"<li>{item}</li>" for item in sec["items"])
            chunks.append(f"<{sec_type}{cls}>\n{li_html}\n</{sec_type}>")
        elif sec_type == "blockquote":
            cls = "" if for_rss else ' class="border-l-4 border-[#2563EB] pl-4 italic text-slate-700 my-6"'
            chunks.append(f"<blockquote{cls}>{sec['text']}</blockquote>")
    return "\n".join(chunks)


def _format_ru_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    months = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля",
        5: "мая", 6: "июня", 7: "июля", 8: "августа",
        9: "сентября", 10: "октября", 11: "ноября", 12: "декабря",
    }
    return f"{dt.day} {months[dt.month]} {dt.year}"


def _format_rfc2822(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=MSK_TZ)
    return format_datetime(dt)


_METRIKA_SNIPPET = """    <!-- Yandex.Metrika counter -->
    <script type="text/javascript">
        (function(m,e,t,r,i,k,a){
            m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
            m[i].l=1*new Date();
            for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
            k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
        })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=113958309', 'ym');

        ym(113958309, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
    </script>
    <noscript><div><img src="https://mc.yandex.ru/watch/113958309" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
    <!-- /Yandex.Metrika counter -->"""


def _render_header(subtitle: str, cta_href: str, cta_label: str) -> str:
    return f"""    <header class="sticky top-0 z-50 bg-[#F8FAFC]/90 backdrop-blur-md border-b border-slate-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <a href="../index.html" class="flex items-center gap-3 group">
                <div class="w-10 h-10 rounded-xl bg-[#2563EB] flex items-center justify-center text-white shadow-sm group-hover:scale-105 transition-transform" aria-hidden="true">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                    </svg>
                </div>
                <div>
                    <span class="font-black text-xl tracking-tight text-[#0F172A]">Local<span class="text-[#2563EB]">Web</span></span>
                    <span class="hidden sm:block text-[11px] text-slate-500 font-medium leading-none">{html.escape(subtitle)}</span>
                </div>
            </a>

            <nav aria-label="Навигация по блогу" class="hidden md:flex items-center gap-7 text-sm font-semibold text-slate-600">
                <a href="index.html" class="hover:text-[#2563EB] transition-colors">Все статьи</a>
                <a href="../index.html#offers" class="hover:text-[#2563EB] transition-colors">Условия</a>
                <a href="../index.html#compare" class="hover:text-[#2563EB] transition-colors">Сравнение</a>
                <a href="../index.html" class="hover:text-[#2563EB] transition-colors">Главная</a>
            </nav>

            <div class="flex items-center gap-3">
                <a href="../dzen-rss.xml" class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white border border-slate-200 text-xs font-bold text-slate-600 hover:border-blue-300 hover:text-[#2563EB] transition-colors">
                    RSS для Дзена
                </a>
                <a href="{cta_href}" class="bg-[#0F172A] hover:bg-slate-800 text-white text-xs sm:text-sm font-bold px-4 sm:px-5 py-2.5 rounded-xl transition-all shadow-sm">
                    {html.escape(cta_label)}
                </a>
            </div>
        </div>
    </header>"""


def _render_footer() -> str:
    return """    <footer class="bg-[#0F172A] text-slate-300 border-t border-slate-800 py-12 px-4 sm:px-6 lg:px-8 mt-16">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div>
                <a href="../index.html" class="font-black text-xl tracking-tight text-white">Local<span class="text-[#2563EB]">Web</span></a>
                <p class="text-xs text-slate-400 mt-1">Быстрые сайты для малого бизнеса • © 2026 LocalWeb</p>
            </div>
            <div class="flex flex-wrap items-center gap-6 text-sm font-medium">
                <a href="index.html" class="hover:text-white transition-colors">Все статьи</a>
                <a href="../index.html" class="hover:text-white transition-colors">Главная страница</a>
                <a href="../policy.html" class="hover:text-white transition-colors">Политика 152-ФЗ</a>
                <a href="../dzen-rss.xml" class="text-blue-400 hover:text-white transition-colors">RSS-лента</a>
            </div>
        </div>
    </footer>"""


def _build_article_page(article: dict) -> None:
    slug = article["slug"]
    page_url = f"{SITE_URL}/blog/{slug}.html"
    img_url = f"{SITE_URL}/blog/images/{article['image']}"
    title_esc = html.escape(article["title"])
    desc_esc = html.escape(article["description"])
    cat_esc = html.escape(article["category"])
    caption_esc = html.escape(article["image_caption"])
    iso_date = datetime.strptime(article["pub_date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=MSK_TZ).isoformat()
    ru_date = _format_ru_date(article["pub_date"])
    body_html = _render_sections_html(article["sections"], for_rss=False)

    page_html = f"""<!DOCTYPE html>
<html lang="ru" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_esc} — Блог LocalWeb</title>
    <meta name="description" content="{desc_esc}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{page_url}">
    <link rel="alternate" type="application/rss+xml" title="LocalWeb — Блог для бизнеса (Дзен RSS)" href="{SITE_URL}/dzen-rss.xml">
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <meta name="theme-color" content="#2563EB">

    <meta property="og:type" content="article">
    <meta property="og:url" content="{page_url}">
    <meta property="og:title" content="{title_esc}">
    <meta property="og:description" content="{desc_esc}">
    <meta property="og:image" content="{img_url}">
    <meta property="og:image:width" content="1080">
    <meta property="og:image:height" content="1080">
    <meta property="og:site_name" content="LocalWeb">
    <meta property="og:locale" content="ru_RU">

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{title_esc}",
      "description": "{desc_esc}",
      "image": "{img_url}",
      "datePublished": "{iso_date}",
      "author": {{
        "@type": "Person",
        "name": "Александр Яровенко"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "LocalWeb",
        "url": "{SITE_URL}/"
      }},
      "mainEntityOfPage": "{page_url}"
    }}
    </script>

    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="../styles.css">
{_METRIKA_SNIPPET}
</head>
<body class="bg-[#F8FAFC] text-[#0F172A] min-h-screen flex flex-col">
{_render_header("Блог для локального бизнеса", "../index.html#form", "Обсудить сайт")}

    <main class="flex-1 py-10 sm:py-14 px-4 sm:px-6 lg:px-8">
        <article class="max-w-3xl mx-auto bg-white border border-slate-200 rounded-3xl p-6 sm:p-10 shadow-sm">
            <nav aria-label="Хлебные крошки" class="flex items-center gap-2 text-xs font-semibold text-slate-500 mb-6">
                <a href="../index.html" class="hover:text-[#2563EB]">Главная</a>
                <span>/</span>
                <a href="index.html" class="hover:text-[#2563EB]">Блог</a>
                <span>/</span>
                <span class="text-[#2563EB]">{cat_esc}</span>
            </nav>

            <header class="mb-8">
                <div class="flex flex-wrap items-center gap-3 text-xs font-semibold text-slate-500 mb-4">
                    <span class="px-3 py-1 rounded-full bg-blue-50 text-[#2563EB] border border-blue-200/70">{cat_esc}</span>
                    <time datetime="{iso_date}">{ru_date}</time>
                    <span>•</span>
                    <span>Время чтения: {html.escape(article['read_time'])}</span>
                </div>
                <h1 class="text-2xl sm:text-4xl font-black text-[#0F172A] tracking-tight leading-tight mb-4">
                    {title_esc}
                </h1>
                <p class="text-base sm:text-lg text-slate-600 leading-relaxed">
                    {desc_esc}
                </p>
            </header>

            <figure class="mb-8">
                <img src="images/{article['image']}" width="1080" height="1080" alt="{caption_esc}" class="w-full max-w-xl mx-auto rounded-2xl border border-slate-200 shadow-sm">
                <figcaption class="text-center text-xs text-slate-500 mt-3">{caption_esc}</figcaption>
            </figure>

            <div class="prose-content">
{body_html}
            </div>

            <div class="mt-10 pt-6 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div class="text-xs text-slate-500">
                    Автор: <strong class="text-slate-700">Александр Яровенко</strong> • Студия <a href="../index.html" class="text-[#2563EB] hover:underline font-semibold">LocalWeb</a>
                </div>
                <a href="index.html" class="inline-flex items-center gap-1.5 text-sm font-bold text-[#2563EB] hover:text-blue-700">
                    ← Все статьи блога
                </a>
            </div>
        </article>
    </main>

{_render_footer()}
</body>
</html>
"""
    (BLOG_DIR / f"{slug}.html").write_text(page_html, encoding="utf-8")


def _build_blog_index(articles_sorted: list[dict]) -> None:
    cards: list[str] = []
    for art in articles_sorted:
        title_esc = html.escape(art["title"])
        desc_esc = html.escape(art["description"])
        cat_esc = html.escape(art["category"])
        ru_date = _format_ru_date(art["pub_date"])
        cards.append(
            f"""            <a href="{art['slug']}.html" class="card-glass p-5 flex flex-col justify-between group">
                <div>
                    <div class="aspect-square w-full overflow-hidden rounded-xl border border-slate-200/80 mb-4 bg-slate-50">
                        <img src="images/{art['image']}" alt="{title_esc}" loading="lazy" class="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300">
                    </div>
                    <div class="flex items-center justify-between gap-2 text-xs font-semibold text-slate-500 mb-2.5">
                        <span class="px-2.5 py-0.5 rounded-full bg-blue-50 text-[#2563EB] border border-blue-200/60">{cat_esc}</span>
                        <span>{ru_date}</span>
                    </div>
                    <h2 class="text-lg font-extrabold text-[#0F172A] leading-snug mb-2 group-hover:text-[#2563EB] transition-colors">
                        {title_esc}
                    </h2>
                    <p class="text-sm text-slate-600 leading-relaxed line-clamp-3">
                        {desc_esc}
                    </p>
                </div>
                <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-[#2563EB]">
                    <span>Читать статью</span>
                    <span>{html.escape(art['read_time'])} →</span>
                </div>
            </a>"""
        )

    index_html = f"""<!DOCTYPE html>
<html lang="ru" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Блог LocalWeb — Полезные статьи о сайтах, 152-ФЗ и привлечении клиентов</title>
    <meta name="description" content="Практические гайды для владельцев малого бизнеса: как не переплачивать за конструкторы, настроить 152-ФЗ, SEO, Яндекс Метрику и приём заявок в Telegram.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{SITE_URL}/blog/">
    <link rel="alternate" type="application/rss+xml" title="LocalWeb — Блог для бизнеса (Дзен RSS)" href="{SITE_URL}/dzen-rss.xml">
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <meta name="theme-color" content="#2563EB">

    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}/blog/">
    <meta property="og:title" content="Блог LocalWeb — Статьи и гайды для малого бизнеса">
    <meta property="og:description" content="Разборы технических и маркетинговых задач малого бизнеса в интернете.">
    <meta property="og:image" content="{SITE_URL}/og-image.png">

    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="../styles.css">
{_METRIKA_SNIPPET}
</head>
<body class="bg-[#F8FAFC] text-[#0F172A] min-h-screen flex flex-col">
{_render_header("Блог для локального бизнеса", "../index.html#form", "Заказать сайт")}

    <main class="flex-1 py-12 sm:py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div class="max-w-3xl mb-12">
            <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200/70 text-[#2563EB] text-xs font-bold mb-4">
                Практическая база знаний • {len(articles_sorted)} статей
            </div>
            <h1 class="text-3xl sm:text-5xl font-black text-[#0F172A] tracking-tight leading-tight mb-4">
                Блог о быстрых сайтах и заявках для малого бизнеса
            </h1>
            <p class="text-base sm:text-lg text-slate-600 leading-relaxed">
                Разбираем на практике, как уйти от переплат за подписочные конструкторы, соблюсти 152-ФЗ, исправить базовые ошибки SEO и не терять обращения из рекламы и карт.
            </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
{chr(10).join(cards)}
        </div>
    </main>

{_render_footer()}
</body>
</html>
"""
    (BLOG_DIR / "index.html").write_text(index_html, encoding="utf-8")


def _build_dzen_rss(articles_sorted: list[dict], image_sizes: dict[str, int], draft_mode: bool = False) -> str:
    items_xml: list[str] = []
    for art in articles_sorted:
        link = f"{SITE_URL}/blog/{art['slug']}.html"
        img_url = f"{SITE_URL}/blog/images/{art['image']}"
        img_len = image_sizes[art["image"]]
        pub_date = _format_rfc2822(art["pub_date"])

        draft_tag = "\n      <category>native-draft</category>" if draft_mode else ""
        figure_html = (
            f'<figure>'
            f'<img src="{img_url}" width="1080" height="1080">'
            f'<figcaption>{html.escape(art["image_caption"])}</figcaption>'
            f'</figure>'
        )
        content_body = _render_sections_html(art["sections"], for_rss=True)
        cdata_html = f"{figure_html}\n{content_body}".replace("]]>", "]]]]><![CDATA[>")

        items_xml.append(
            f"""    <item>
      <title>{html.escape(art['title'])}</title>
      <link>{link}</link>
      <pdalink>{link}</pdalink>
      <guid isPermaLink="false">{html.escape(art['id'])}</guid>
      <pubDate>{pub_date}</pubDate>
      <author>Александр Яровенко</author>
      <media:rating scheme="urn:simple">nonadult</media:rating>
      <category>format-article</category>{draft_tag}
      <category>{html.escape(art['category'])}</category>
      <description>{html.escape(art['description'])}</description>
      <enclosure url="{img_url}" length="{img_len}" type="image/png"/>
      <content:encoded><![CDATA[
{cdata_html}
      ]]></content:encoded>
    </item>"""
        )

    last_build = _format_rfc2822(articles_sorted[0]["pub_date"])
    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:media="http://search.yahoo.com/mrss/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:georss="http://www.georss.org/georss">
  <channel>
    <title>LocalWeb — Сайты и маркетинг для малого бизнеса</title>
    <link>{SITE_URL}/blog/</link>
    <description>Практические статьи о создании быстрых сайтов, SEO, аналитике и 152-ФЗ для локального бизнеса.</description>
    <language>ru</language>
    <lastBuildDate>{last_build}</lastBuildDate>
    <atom:link href="{SITE_URL}/dzen-rss.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    RSS_PATH.write_text(rss_xml, encoding="utf-8")
    return rss_xml


def _update_sitemap(articles_sorted: list[dict]) -> None:
    base_entries = [
        (f"{SITE_URL}/", "2026-10-29", "weekly", "1.0"),
        (f"{SITE_URL}/presentation.html", "2026-10-29", "monthly", "0.8"),
        (f"{SITE_URL}/LocalWeb_Presentation.pdf", "2026-10-29", "monthly", "0.7"),
        (f"{SITE_URL}/policy.html", "2026-10-29", "yearly", "0.3"),
        (f"{SITE_URL}/blog/", articles_sorted[0]["pub_date"][:10], "weekly", "0.9"),
    ]
    for art in articles_sorted:
        base_entries.append(
            (f"{SITE_URL}/blog/{art['slug']}.html", art["pub_date"][:10], "monthly", "0.7")
        )

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, changefreq, priority in base_entries:
        lines.extend([
            "  <url>",
            f"    <loc>{loc}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            f"    <changefreq>{changefreq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ])
    lines.append("</urlset>")
    SITEMAP_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _validate_feed(rss_xml: str) -> None:
    """Проверяет XML-валидность и ключевые требования Дзена к RSS-ленте."""
    root = ET.fromstring(rss_xml)
    items = root.findall("./channel/item")
    if len(items) < 10:
        raise ValueError(f"Для подключения Дзен требует минимум 10 материалов, сейчас: {len(items)}")

    for item in items:
        title = (item.findtext("title") or "").strip()
        if not title or len(title) > 200 or title.endswith("."):
            raise ValueError(f"Некорректный заголовок статьи для Дзена: '{title}'")
        enclosure = item.find("enclosure")
        if enclosure is None or not enclosure.attrib.get("url"):
            raise ValueError(f"Отсутствует <enclosure> у статьи '{title}'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Сборка блога и RSS-ленты Дзена для local-web.ru")
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Добавлять <category>native-draft</category> (сохранять в черновиках Студии Дзена)",
    )
    args = parser.parse_args()

    articles_sorted = sorted(ARTICLES, key=lambda x: x["pub_date"], reverse=True)
    image_sizes = _sync_images()

    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    for art in articles_sorted:
        _build_article_page(art)
    _build_blog_index(articles_sorted)

    rss_xml = _build_dzen_rss(articles_sorted, image_sizes, draft_mode=args.draft)
    _validate_feed(rss_xml)
    _update_sitemap(articles_sorted)

    print(f"[OK] Собрано статей: {len(articles_sorted)} -> {BLOG_DIR}")
    print(f"[OK] Сгенерирован валидный фид Дзена: {RSS_PATH}")
    print(f"[OK] Обновлён Sitemap: {SITEMAP_PATH}")


if __name__ == "__main__":
    main()
