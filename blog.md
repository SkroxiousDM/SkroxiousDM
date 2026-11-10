---
title: Development blog
permalink: /blog/
---
Design notes, rules discussions, playtest updates, and publication announcements.

{% for post in site.posts %}
<article>
  <h2><a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></h2>
  <p><time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: '%B %-d, %Y' }}</time></p>
  {{ post.excerpt }}
  <p><a href="{{ post.url | relative_url }}">Read the post</a></p>
</article>
{% else %}
<p>The first development post is coming soon.</p>
{% endfor %}
