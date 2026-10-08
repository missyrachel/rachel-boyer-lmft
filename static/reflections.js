'use strict';
const search = document.getElementById('search-reflections');
const cards = Array.from(document.querySelectorAll('.reflection-card'));
const status = document.getElementById('search-status');
const empty = document.getElementById('no-results');
function filterReflections() {
  const words = search.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const card of cards) {
    const haystack = card.dataset.search.toLocaleLowerCase();
    card.hidden = !words.every(word => haystack.includes(word));
    if (!card.hidden) visible++;
  }
  status.textContent = `${visible} reflection${visible === 1 ? '' : 's'}`;
  empty.hidden = visible !== 0;
}
search.addEventListener('input', filterReflections);
filterReflections();
