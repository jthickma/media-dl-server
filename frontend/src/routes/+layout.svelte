<script>
  import { page } from '$app/stores';
  let { children } = $props();
  const tabs = [
    { href: '/', label: 'Download' },
    { href: '/files', label: 'Files' },
    { href: '/config', label: 'Config' },
    { href: '/cookies', label: 'Cookies' }
  ];
</script>

<div class="app">
  <header>
    <h1>claude-media-dl</h1>
    <nav>
      {#each tabs as t}
        <a href={t.href} class:active={$page.url.pathname === t.href}>{t.label}</a>
      {/each}
    </nav>
  </header>
  <main>{@render children()}</main>
</div>

<style>
  :global(html, body) { margin: 0; padding: 0; background: #0e1116; color: #e6edf3; font-family: -apple-system, system-ui, sans-serif; }
  :global(*) { box-sizing: border-box; }
  :global(button, input, select, textarea) { font-family: inherit; font-size: 14px; }
  :global(a) { color: #4ea1ff; text-decoration: none; }
  :global(a:hover) { text-decoration: underline; }
  :global(button) {
    background: #21262d; color: #e6edf3; border: 1px solid #30363d; border-radius: 6px;
    padding: 6px 12px; cursor: pointer;
  }
  :global(button:hover) { background: #30363d; }
  :global(button.primary) { background: #238636; border-color: #2ea043; }
  :global(button.primary:hover) { background: #2ea043; }
  :global(input[type=text], input[type=url], select, textarea) {
    background: #0d1117; color: #e6edf3; border: 1px solid #30363d;
    border-radius: 6px; padding: 6px 10px; width: 100%;
  }
  .app { min-height: 100vh; display: flex; flex-direction: column; }
  header {
    padding: 12px 24px; border-bottom: 1px solid #21262d;
    display: flex; align-items: center; gap: 24px;
  }
  h1 { margin: 0; font-size: 18px; font-weight: 600; }
  nav { display: flex; gap: 4px; }
  nav a {
    padding: 6px 12px; border-radius: 6px; color: #8b949e; text-decoration: none;
  }
  nav a.active { background: #21262d; color: #e6edf3; }
  nav a:hover { color: #e6edf3; text-decoration: none; }
  main { flex: 1; padding: 24px; max-width: 1400px; width: 100%; margin: 0 auto; }
</style>
