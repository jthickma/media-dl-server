<script>
  import { onMount } from 'svelte';
  import { api, fmtBytes } from '$lib/api.js';

  let cwd = $state('');
  let listing = $state({ items: [], parent: '', path: '' });
  let selected = $state(null);

  async function load(p = '') {
    cwd = p;
    listing = await api(`/api/files?path=${encodeURIComponent(p)}`);
    selected = null;
  }

  function open(item) {
    if (item.is_dir) {
      load(item.path);
    } else {
      selected = item;
    }
  }

  async function del(item) {
    if (!confirm(`Delete ${item.name}?`)) return;
    await api(`/api/files?path=${encodeURIComponent(item.path)}`, { method: 'DELETE' });
    load(cwd);
  }

  function mediaType(mime) {
    if (!mime) return 'other';
    if (mime.startsWith('video/')) return 'video';
    if (mime.startsWith('audio/')) return 'audio';
    if (mime.startsWith('image/')) return 'image';
    if (mime === 'application/pdf') return 'pdf';
    if (mime.startsWith('text/')) return 'text';
    return 'other';
  }

  function iconFor(mime) {
    if (!mime) return '📄';
    if (mime.startsWith('video/')) return '🎬';
    if (mime.startsWith('audio/')) return '🎵';
    if (mime.startsWith('image/')) return '🖼';
    if (mime === 'application/pdf') return '📕';
    if (mime.startsWith('text/')) return '📝';
    return '📄';
  }

  let textContent = $state('');
  $effect(() => {
    if (selected && mediaType(selected.mime) === 'text') {
      fetch(`/media/${encodeURI(selected.path)}`).then(r => r.text()).then(t => textContent = t);
    } else {
      textContent = '';
    }
  });

  onMount(() => {
    const params = new URLSearchParams(location.search);
    const open = params.get('open');
    if (open) {
      const dir = open.split('/').slice(0, -1).join('/');
      load(dir).then(() => {
        selected = listing.items.find(i => i.path === open) || null;
      });
    } else {
      load('');
    }
  });
</script>

<div class="layout">
  <div class="browser card">
    <div class="bread">
      <button onclick={() => load('')} disabled={cwd === ''}>/</button>
      {#if cwd}
        <span>/ {cwd}</span>
        <button onclick={() => load(listing.parent)}>↑ up</button>
      {/if}
      <a class="zip" href="/api/files/zip?path={encodeURIComponent(cwd)}" title="Download current folder as zip" download style="margin-left:auto">⬇ zip</a>
      <button onclick={() => load(cwd)} title="Refresh">⟳</button>
    </div>
    {#if listing.items.length === 0}
      <p class="muted">Empty.</p>
    {:else}
      <ul class="files">
        {#each listing.items as item}
          <li class:active={selected?.path === item.path}>
            <button class="entry" onclick={() => open(item)}>
              <span class="ico">{item.is_dir ? '📁' : iconFor(item.mime)}</span>
              <span class="name">{item.name}</span>
              <span class="size">{item.is_dir ? '' : fmtBytes(item.size)}</span>
            </button>
            {#if item.is_dir}
              <a class="zip" href="/api/files/zip?path={encodeURIComponent(item.path)}" title="Download as zip" download>⬇ zip</a>
            {/if}
            <button class="del" onclick={() => del(item)} title="Delete">✕</button>
          </li>
        {/each}
      </ul>
    {/if}
  </div>

  <div class="viewer card">
    {#if !selected}
      <p class="muted center">Select a file to preview.</p>
    {:else}
      {@const t = mediaType(selected.mime)}
      <div class="vhead">
        <span class="vname">{selected.name}</span>
        <a href="/media/{encodeURI(selected.path)}" download>Download</a>
      </div>
      <div class="vbody">
        {#if t === 'video'}
          <video controls src="/media/{encodeURI(selected.path)}"></video>
        {:else if t === 'audio'}
          <audio controls src="/media/{encodeURI(selected.path)}"></audio>
        {:else if t === 'image'}
          <img src="/media/{encodeURI(selected.path)}" alt={selected.name} />
        {:else if t === 'pdf'}
          <embed src="/media/{encodeURI(selected.path)}" type="application/pdf" />
        {:else if t === 'text'}
          <pre class="text">{textContent}</pre>
        {:else}
          <p class="muted">No preview. <a href="/media/{encodeURI(selected.path)}" download>Download</a> ({selected.mime})</p>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .layout { display: grid; grid-template-columns: 320px 1fr; gap: 16px; height: calc(100vh - 130px); }
  @media (max-width: 800px) { .layout { grid-template-columns: 1fr; height: auto; } }
  .card { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 12px; overflow: hidden; display: flex; flex-direction: column; }
  .bread { display: flex; gap: 6px; align-items: center; margin-bottom: 8px; font-size: 13px; }
  .bread span { color: #8b949e; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .files { list-style: none; padding: 0; margin: 0; overflow-y: auto; flex: 1; }
  .files li { display: flex; align-items: center; }
  .files li:hover { background: #1c2128; }
  .files li.active { background: #21262d; }
  .entry {
    flex: 1; background: none; border: none; text-align: left; padding: 6px 8px;
    display: flex; align-items: center; gap: 8px; color: inherit; cursor: pointer; min-width: 0;
  }
  .entry:hover { background: none; }
  .ico { width: 18px; }
  .name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; }
  .size { color: #8b949e; font-size: 11px; }
  .del { background: none; border: none; color: #6e7681; padding: 4px 8px; cursor: pointer; }
  .del:hover { color: #da3633; background: none; }
  .zip {
    color: #8b949e; font-size: 11px; text-decoration: none; padding: 4px 8px;
    border: 1px solid #30363d; border-radius: 4px; white-space: nowrap;
  }
  .zip:hover { color: #e6edf3; background: #21262d; text-decoration: none; }
  .vhead { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #21262d; }
  .vname { flex: 1; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .vbody { flex: 1; display: flex; align-items: center; justify-content: center; overflow: auto; }
  .vbody video, .vbody img, .vbody embed { max-width: 100%; max-height: 100%; }
  .vbody embed { width: 100%; height: 100%; }
  .vbody audio { width: 100%; }
  .text { width: 100%; max-height: 100%; overflow: auto; background: #0d1117; padding: 12px; border-radius: 6px; font-size: 12px; white-space: pre-wrap; }
  .center { display: flex; align-items: center; justify-content: center; height: 100%; }
  .muted { color: #8b949e; }
</style>
