const fs = require('fs');
const path = require('path');
const { fireEvent } = require('@testing-library/dom');

jest.useFakeTimers();

describe('Global search', () => {
  beforeEach(() => {
    const indexHtml = fs.readFileSync(path.resolve(__dirname, '..', 'index.html'), 'utf8');
    document.documentElement.innerHTML = indexHtml;
    // Load app.js into the test environment scope
    const appJs = fs.readFileSync(path.resolve(__dirname, '..', 'app.js'), 'utf8');
    // Evaluate app.js in this JSDOM environment; it will attach helpers to window.__verityTest
    // eslint-disable-next-line no-eval
    eval(appJs);
  });

  test('search input and results exist and are hidden initially', () => {
    expect(document.getElementById('search-input')).not.toBeNull();
    expect(document.getElementById('search-results')).not.toBeNull();
    // Setup search functionality
    window.__verityTest.setupGlobalSearch();
    const results = document.getElementById('search-results');
    expect(results.classList.contains('hidden')).toBe(true);
  });

  test('keyboard navigation selects items and Enter activates selection', () => {
    window.__verityTest.setupGlobalSearch();
    const searchInput = document.getElementById('search-input');
    const results = document.getElementById('search-results');

    // Provide NAV_ITEMS for predictable results
    window.NAV_ITEMS = [{ section: 'Overview', items: [ { id: 'dashboard', icon: 'dashboard', label: 'Dashboard' }, { id: 'verify', icon: 'verify', label: 'Verify Content' } ] }];

    // Type into the input
    searchInput.value = 'ver';
    fireEvent.input(searchInput);
    // Advance timers for debounce
    jest.advanceTimersByTime(250);

    const items = results.querySelectorAll('.search-item');
    expect(items.length).toBeGreaterThan(0);

    // Arrow down to first item
    fireEvent.keyDown(searchInput, { key: 'ArrowDown' });
    expect(results.querySelector('.search-item.selected')).not.toBeNull();

    // Press Enter -> should activate and hide results
    fireEvent.keyDown(searchInput, { key: 'Enter' });
    expect(results.classList.contains('hidden')).toBe(true);
    expect(searchInput.value).toBe('');
  });
});