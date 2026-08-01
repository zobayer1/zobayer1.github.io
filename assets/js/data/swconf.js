---
layout: compress
permalink: '/:path/swconf.js'
# Note that this file will be fetched by the ServiceWorker, so it will not be cached.
---

{%- comment -%}
  Local override of jekyll-theme-chirpy 7.5.0's swconf.js. The only change from
  upstream is the block marked `LOCAL:` below, which keeps the pageviews Worker
  out of the service worker's cache. Re-apply it after a theme bump.

  This matters: the service worker is cache-first (`caches.match(req) || fetch(req)`)
  and ignores Cache-Control entirely, so without this the Worker's response would be
  stored on first visit and replayed forever — freezing every view count until the
  next site deploy rotates `cacheName`.
{%- endcomment -%}

const swconf = {
  {% if site.pwa.cache.enabled %}
    cacheName: 'chirpy-{{ "now" | date: "%s" }}',

    {%- comment -%} Resources added to the cache during PWA installation. {%- endcomment -%}
    resources: [
      '{{ "/assets/css/:THEME.css" | replace: ':THEME', site.theme | relative_url }}',
      '{{ "/" | relative_url }}',
      {% for tab in site.tabs %}
        '{{- tab.url | relative_url -}}',
      {% endfor %}

      {% assign cache_list = site.static_files | where: 'swcache', true %}
      {% for file in cache_list %}
        '{{ file.path | relative_url }}'{%- unless forloop.last -%},{%- endunless -%}
      {% endfor %}
    ],

    interceptor: {
      {%- comment -%} URLs containing the following paths will not be cached. {%- endcomment -%}
      paths: [
        {% for path in site.pwa.cache.deny_paths %}
          {% unless path == empty %}
            '{{ path | relative_url }}'{%- unless forloop.last -%},{%- endunless -%}
          {% endunless  %}
        {% endfor %}
      ],

      {%- comment -%} URLs containing the following prefixes will not be cached. {%- endcomment -%}
      urlPrefixes: [
        {% if site.analytics.goatcounter.id != nil and site.pageviews.provider == 'goatcounter' %}
          'https://{{ site.analytics.goatcounter.id }}.goatcounter.com/counter/',
        {% endif %}

        {%- comment -%} LOCAL: the pageviews Worker — see the note at the top. {%- endcomment -%}
        {% if site.pageviews.proxy and site.pageviews.proxy != empty %}
          '{{ site.pageviews.proxy }}'
        {% endif %}
      ]
    },

    purge: false
  {% else %}
    purge: true
  {% endif %}
};
