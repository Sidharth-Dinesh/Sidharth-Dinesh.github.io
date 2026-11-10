/* Progressive enhancements: content and navigation also work without JavaScript. */
document.documentElement.classList.add('js');
const menu = document.querySelector('[data-menu-toggle]');
const navigation = document.getElementById('site-navigation');
if (menu && navigation) {
  function closeMenu() {
    menu.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('open');
  }
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    navigation.classList.toggle('open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menu.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!event.target.closest('.site-header')) closeMenu();
  });
}
for (const button of document.querySelectorAll('[data-copy-citation]')) {
  button.addEventListener('click', async () => {
    const code = document.getElementById(button.dataset.copyCitation);
    const status = button.parentElement.querySelector('[role="status"]');
    try {
      await navigator.clipboard.writeText(code.textContent);
      status.textContent = 'Citation copied.';
    } catch {
      const range = document.createRange();
      range.selectNodeContents(code);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = 'Citation selected. Press Ctrl+C or Command+C to copy.';
    }
  });
}

// GIF controls, with a still frame by default when reduced motion is preferred.
for (const button of document.querySelectorAll('.animation-toggle')) {
  const figure=button.closest('figure');
  const image=figure.querySelector('img[data-animation-src]');
  const source=figure.querySelector('source');
  let paused=window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function update(){
    const url=paused?image.dataset.stillSrc:image.dataset.animationSrc;
    image.src=url;if(source)source.srcset=url;
    button.textContent=paused?'Play animation':'Pause animation';
    button.setAttribute('aria-pressed',String(paused));
  }
  button.hidden=false;update();
  button.addEventListener('click',()=>{paused=!paused;update();});
}

document.querySelectorAll('a[href]').forEach(link => {
  const url = new URL(link.href, window.location.href);

  if (
    ['http:', 'https:'].includes(url.protocol) &&
    (url.origin !== window.location.origin ||
      url.pathname.toLowerCase().endsWith('.pdf'))
  ) {
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
  }
});