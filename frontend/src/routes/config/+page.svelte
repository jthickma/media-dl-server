<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api.js';

  let active = $state('yt-dlp');
  let content = $state('');
  let path = $state('');
  let status = $state('');
  let dirty = $state(false);

  async function load(name) {
    active = name;
    status = 'loading...';
    const r = await api(`/api/config/${name}`);
    content = r.content;
    path = r.path;
    dirty = false;
    status = '';
  }

  async function save() {
    status = 'saving...';
    await api(`/api/config/${active}`, { method: 'PUT', body: JSON.stringify({ content }) });
    dirty = false;
    status = 'saved ✓';
    setTimeout(() => status = '', 2000);
  }

  onMount(() => load('yt-dlp'));
</script>

<div class="card">
  <div class="head">
    <div class="tabs">
      <button class:active={active === 'yt-dlp'} onclick={() => load('yt-dlp')}>yt-dlp.conf</button>
      <button class:active={active === 'gallery-dl'} onclick={() => load('gallery-dl')}>gallery-dl.conf</button>
    </div>
    <span class="path muted">{path}</span>
    <span class="status">{status}</span>
    <button class="primary" onclick={save} disabled={!dirty}>Save</button>
  </div>
  <textarea
    bind:value={content}
    oninput={() => dirty = true}
    spellcheck="false"
    placeholder="# config..."
  ></textarea>
  <p class="hint muted">
    {#if active === 'yt-dlp'}
      One option per line, e.g. <code>-f bestvideo+bestaudio</code>, <code>--write-subs</code>.
      <a href="https://github.com/yt-dlp/yt-dlp#configuration" target="_blank">Docs</a>
    {:else}
      JSON. <a href="https://github.com/mikf/gallery-dl/blob/master/docs/configuration.rst" target="_blank">Docs</a>
    {/if}
  </p>
</div>

<style>
  .card { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 16px; }
  .head { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
  .tabs { display: flex; gap: 4px; }
  .tabs button.active { background: #1f6feb; border-color: #1f6feb; }
  .path { font-family: monospace; font-size: 12px; flex: 1; }
  .status { color: #2ea043; font-size: 12px; }
  textarea {
    width: 100%; min-height: 480px; font-family: 'SF Mono', Menlo, monospace;
    font-size: 13px; line-height: 1.5; tab-size: 2;
  }
  .hint { font-size: 12px; margin-top: 8px; }
  code { background: #21262d; padding: 1px 6px; border-radius: 4px; font-size: 11px; }
  .muted { color: #8b949e; }
</style>
