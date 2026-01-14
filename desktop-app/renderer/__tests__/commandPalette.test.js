const fs = require('fs');
const path = require('path');
const { fireEvent } = require('@testing-library/dom');

jest.useFakeTimers();

describe('Command palette', () => {
  beforeEach(() => {
    const indexHtml = fs.readFileSync(path.resolve(__dirname, '..', 'index.html'), 'utf8');
    document.documentElement.innerHTML = indexHtml;
    const appJs = fs.readFileSync(path.resolve(__dirname, '..', 'app.js'), 'utf8');
    // eslint-disable-next-line no-eval
    eval(appJs);
  });

  test('Ctrl/Cmd+K toggles palette and typing filters results', () => {
    window.NAV_ITEMS = [{ section: 'Overview', items: [ { id: 'dashboard', icon: 'dashboard', label: 'Dashboard' }, { id: 'verify', icon: 'verify', label: 'Verify Content' } ] }];

    window.__verityTest.setupCommandPalette();
    const cmd = document.getElementById('cmd');
    const input = document.getElementById('cmd-input');
    // simulate keydown Ctrl+K when not focused in an input
    const e = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true });
    document.dispatchEvent(e);
    expect(cmd.classList.contains('active')).toBe(true);

    // typing filters
    input.value = 'verify';
    fireEvent.input(input);
    const results = document.getElementById('cmd-results');
    expect(results.textContent.toLowerCase()).toContain('verify');
  });

  test('Selecting an item navigates and closes palette', () => {
    window.NAV_ITEMS = [{ section: 'Overview', items: [ { id: 'dashboard', icon: 'dashboard', label: 'Dashboard' } ] }];
    window.navigate = jest.fn();

    window.__verityTest.setupCommandPalette();
    const e = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true });
    document.dispatchEvent(e);

    // Ensure suggestions rendered
    const input = document.getElementById('cmd-input');
    input.value = 'dash';
    fireEvent.input(input);

    const item = document.querySelector('.cmd-item');
    expect(item).not.toBeNull();
    fireEvent.click(item);

    expect(window.navigate).toHaveBeenCalledWith('dashboard');
    const cmd = document.getElementById('cmd');
    expect(cmd.classList.contains('active')).toBe(false);
  });
});