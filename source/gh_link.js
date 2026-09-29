<script>
/* On GitHub Pages (<user>.github.io/<repo>/...) turn [data-gh] notes into links to the project repository. */
(() => {
  const host = location.hostname.toLowerCase();
  if (!host.endsWith('.github.io')) return;
  const user = host.slice(0, -'.github.io'.length);
  const seg = location.pathname.split('/').filter(Boolean);
  const repo = seg.length && !/\.[a-z0-9]+$/i.test(seg[0]) ? seg[0] : host;
  const base = 'https://github.com/' + user + '/' + repo;
  const tail = {issues: '/issues', 'new-issue': '/issues/new', repo: ''};
  document.querySelectorAll('[data-gh]').forEach(el => {
    const a = document.createElement('a');
    a.href = base + (tail[el.dataset.gh] ?? '');
    a.innerHTML = el.innerHTML;
    if (el.className) a.className = el.className;
    el.replaceWith(a);
  });
})();
</script>
