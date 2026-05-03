<script>
  import { onMount } from 'svelte';
  import { api, jobSocket } from '$lib/api.js';

  let url = $state('');
  let tool = $state('auto');
  let cookies = $state('');
  let cookieList = $state([]);
  let jobs = $state([]);
  let activeId = $state(null);
  let liveJob = $state(null);
  let liveLog = $state([]);
  let ws = null;

  async function refreshJobs() {
    jobs = await api('/api/jobs');
    jobs.sort((a, b) => b.id.localeCompare(a.id));
  }

  async function refreshCookies() {
    cookieList = await api('/api/cookies');
  }

  onMount(() => {
    refreshJobs();
    refreshCookies();
    const t = setInterval(refreshJobs, 4000);
    return () => { clearInterval(t); ws?.close(); };
  });

  async function submit() {
    if (!url.trim()) return;
    const body = { url: url.trim() };
    if (tool !== 'auto') body.tool = tool;
    if (cookies) body.cookies = cookies;
    const res = await api('/api/download', { method: 'POST', body: JSON.stringify(body) });
    url = '';
    await refreshJobs();
    openJob(res.id);
  }

  function openJob(id) {
    ws?.close();
    liveLog = [];
    activeId = id;
    liveJob = jobs.find(j => j.id === id) || null;
    ws = jobSocket(id, (msg) => {
      if (msg.type === 'status' || msg.type === 'progress') {
        liveJob = msg.data;
        const i = jobs.findIndex(j => j.id === id);
        if (i >= 0) jobs[i] = msg.data;
      } else if (msg.type === 'log') {
        liveLog = [...liveLog.slice(-400), msg.line];
      }
    });
  }
</script>

<section class="grid">
  <div class="card">
    <h2>New download</h2>
    <form onsubmit={(e) => { e.preventDefault(); submit(); }}>
      <label>URL
        <input type="url" bind:value={url} placeholder="https://..." required />
      </label>
      <div class="row">
        <label>Tool
          <select bind:value={tool}>
            <option value="auto">auto-detect</option>
            <option value="yt-dlp">yt-dlp</option>
            <option value="gallery-dl">gallery-dl</option>
          </select>
        </label>
        <label>Cookies
          <select bind:value={cookies}>
            <option value="">(none)</option>
            {#each cookieList as c}<option value={c}>{c}</option>{/each}
          </select>
        </label>
      </div>
      <button class="primary" type="submit">Download</button>
    </form>
  </div>

  <div class="card">
    <h2>Jobs</h2>
    {#if jobs.length === 0}
      <p class="muted">No jobs yet.</p>
    {:else}
      <ul class="jobs">
        {#each jobs as j}
          <li class:active={j.id === activeId} onclick={() => openJob(j.id)}>
            <div class="jrow">
              <span class="status" data-status={j.status}>{j.status}</span>
              <span class="url" title={j.url}>{j.url}</span>
            </div>
            <div class="bar"><div style="width: {j.progress}%"></div></div>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</section>

{#if liveJob}
  <section class="card">
    <h2>Job {liveJob.id} <small class="muted">{liveJob.tool}</small></h2>
    <div class="meta">
      <span>Status: <b data-status={liveJob.status}>{liveJob.status}</b></span>
      <span>Progress: {liveJob.progress?.toFixed?.(1) ?? 0}%</span>
      {#if liveJob.speed}<span>Speed: {liveJob.speed}</span>{/if}
      {#if liveJob.eta}<span>ETA: {liveJob.eta}</span>{/if}
    </div>
    {#if liveJob.error}<div class="error">Error: {liveJob.error}</div>{/if}
    {#if liveJob.files?.length}
      <h3>Files</h3>
      <ul>
        {#each liveJob.files as f}
          <li><a href="/files?open={encodeURIComponent(f)}">{f.split('/').pop()}</a></li>
        {/each}
      </ul>
    {/if}
    <h3>Log</h3>
    <pre class="log">{liveLog.join('\n')}</pre>
  </section>
{/if}

<style>
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
  .card {
    background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 16px;
    margin-bottom: 16px;
  }
  h2 { margin: 0 0 12px; font-size: 16px; }
  h3 { font-size: 13px; margin: 16px 0 6px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; }
  label { display: block; margin-bottom: 12px; font-size: 12px; color: #8b949e; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .muted { color: #8b949e; }
  .jobs { list-style: none; padding: 0; margin: 0; max-height: 320px; overflow-y: auto; }
  .jobs li { padding: 8px; border-radius: 6px; cursor: pointer; }
  .jobs li:hover { background: #1c2128; }
  .jobs li.active { background: #21262d; }
  .jrow { display: flex; gap: 8px; align-items: center; font-size: 13px; }
  .url { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
  .status { font-size: 11px; padding: 2px 6px; border-radius: 4px; background: #30363d; }
  .status[data-status=done] { background: #238636; }
  .status[data-status=error] { background: #da3633; }
  .status[data-status=running] { background: #1f6feb; }
  .bar { height: 4px; background: #21262d; border-radius: 2px; overflow: hidden; margin-top: 4px; }
  .bar > div { height: 100%; background: #2ea043; transition: width 0.2s; }
  .meta { display: flex; gap: 16px; flex-wrap: wrap; font-size: 13px; color: #8b949e; margin-bottom: 8px; }
  b[data-status=done] { color: #2ea043; }
  b[data-status=error] { color: #da3633; }
  b[data-status=running] { color: #4ea1ff; }
  .error { background: #2d1417; border: 1px solid #da3633; padding: 8px; border-radius: 6px; color: #ffabab; }
  .log { background: #0d1117; border: 1px solid #21262d; border-radius: 6px; padding: 12px; max-height: 360px; overflow-y: auto; font-size: 12px; white-space: pre-wrap; }
</style>
