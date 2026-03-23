<script lang="ts">
	import { onMount } from 'svelte';
	import { getKeys, saveKeys, testOneKey } from '$lib/api';

	const PROVIDERS = [
		{ env: 'GROQ_API_KEY', name: 'Groq', hint: 'gsk_...', url: 'https://console.groq.com/keys', tier: '30 RPM / 14,400 req/วัน', desc: 'เร็วที่สุด — แนะนำ' },
		{ env: 'GOOGLE_API_KEY', name: 'Google Gemini', hint: 'AIza...', url: 'https://aistudio.google.com/apikey', tier: '15 RPM / 1M tokens/วัน', desc: 'Google account สมัครทันที' },
		{ env: 'OPENROUTER_API_KEY', name: 'OpenRouter', hint: 'sk-or-...', url: 'https://openrouter.ai/settings/keys', tier: 'โมเดล :free ฟรีถาวร', desc: 'มีโมเดลฟรีเยอะ' },
		{ env: 'CEREBRAS_API_KEY', name: 'Cerebras', hint: 'csk-...', url: 'https://cloud.cerebras.ai/', tier: '30 RPM', desc: 'เร็วมาก' },
		{ env: 'SAMBANOVA_API_KEY', name: 'SambaNova', hint: '...', url: 'https://cloud.sambanova.ai/apis', tier: 'ไม่จำกัด (rate limit)', desc: 'ฟรีไม่จำกัด' },
		{ env: 'NVIDIA_API_KEY', name: 'NVIDIA NIM', hint: 'nvapi-...', url: 'https://build.nvidia.com', tier: '1,000 req ฟรี', desc: 'NVIDIA account' },
		{ env: 'MISTRAL_API_KEY', name: 'Mistral AI', hint: '...', url: 'https://console.mistral.ai/api-keys/', tier: 'ฟรี', desc: 'Mistral models' },
		{ env: 'TOGETHER_API_KEY', name: 'Together AI', hint: '...', url: 'https://api.together.ai/settings/api-keys', tier: '$5 ฟรี', desc: 'เครดิตฟรี' },
		{ env: 'DEEPINFRA_API_KEY', name: 'DeepInfra', hint: '...', url: 'https://deepinfra.com/dash/api_keys', tier: 'ฟรี', desc: 'หลาย models' },
		{ env: 'COHERE_API_KEY', name: 'Cohere', hint: '...', url: 'https://dashboard.cohere.com/api-keys', tier: 'Trial ฟรี', desc: 'Command-R' },
	];

	let keys = $state<Record<string, string>>({});
	let testResults = $state<Record<string, any>>({});
	let saveStatus = $state('');
	let saveTimer: any = null;

	onMount(async () => {
		const d = await getKeys();
		if (d?.keys) keys = d.keys;
	});

	function onInput(env: string, val: string) {
		keys[env] = val;
		clearTimeout(saveTimer);
		saveStatus = 'saving';
		saveTimer = setTimeout(doSave, 1500);
	}

	async function doSave() {
		const clean: Record<string, string> = {};
		for (const [k, v] of Object.entries(keys)) { if (v?.trim()) clean[k] = v.trim(); }
		await saveKeys(clean);
		saveStatus = 'saved';
		setTimeout(() => saveStatus = '', 3000);
	}

	async function doTest(env: string) {
		testResults = { ...testResults, [env]: { status: 'testing' } };
		await doSave();
		const r = await testOneKey(env);
		testResults = { ...testResults, [env]: r || { status: 'error', message: 'เชื่อมต่อไม่ได้' } };
	}

	async function testAll() {
		for (const p of PROVIDERS) {
			if (keys[p.env]?.trim()) {
				await doTest(p.env);
			}
		}
	}
</script>

<div class="flex items-center justify-between mb-6">
	<div>
		<h2 class="text-xl font-bold">🔑 จัดการ API Keys</h2>
		<p class="text-sm mt-1" style="color: var(--text2);">ใส่ key → auto-save | กดทดสอบเพื่อเช็คว่าใช้ได้จริง</p>
	</div>
	<div class="flex items-center gap-3">
		{#if saveStatus === 'saving'}
			<span class="text-sm" style="color: var(--yellow);">⏳ กำลังบันทึก...</span>
		{:else if saveStatus === 'saved'}
			<span class="text-sm" style="color: var(--green);">✅ บันทึกแล้ว!</span>
		{/if}
		<button onclick={testAll}
			class="px-4 py-2 rounded-lg text-sm font-semibold cursor-pointer text-white"
			style="background: var(--accent);">
			🧪 ทดสอบทั้งหมด
		</button>
	</div>
</div>

<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
	{#each PROVIDERS as p}
		{@const hasKey = !!keys[p.env]?.trim()}
		{@const r = testResults[p.env]}
		{@const tested = !!r}
		{@const isOk = r?.status === 'ok'}
		{@const isLimit = r?.status === 'rate_limited'}
		{@const isTesting = r?.status === 'testing'}
		{@const isFail = tested && !isOk && !isLimit && !isTesting}

		<div class="rounded-xl border overflow-hidden transition-all"
			style="background: var(--bg2); border-color: {isOk ? 'var(--green)' : isLimit ? 'var(--yellow)' : isFail ? 'var(--red)' : hasKey ? 'var(--accent)' : 'var(--border)'};">

			<!-- Header -->
			<div class="flex items-center justify-between px-4 py-3"
				style="background: {isOk ? 'rgba(63,185,80,0.08)' : isLimit ? 'rgba(210,153,34,0.08)' : isFail ? 'rgba(248,81,73,0.08)' : 'var(--bg3)'};">
				<div class="flex items-center gap-2">
					{#if isTesting}
						<span class="text-lg animate-spin">⏳</span>
					{:else if isOk}
						<span class="text-lg">✅</span>
					{:else if isLimit}
						<span class="text-lg">⚠️</span>
					{:else if isFail}
						<span class="text-lg">❌</span>
					{:else if hasKey}
						<span class="text-lg">🔑</span>
					{:else}
						<span class="text-lg">⬜</span>
					{/if}
					<span class="font-bold text-base">{p.name}</span>
				</div>
				<div class="flex items-center gap-2">
					<button onclick={() => doTest(p.env)}
						disabled={isTesting || !hasKey}
						class="px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer disabled:opacity-40 text-white"
						style="background: var(--accent);">
						{isTesting ? '⏳' : '🧪 ทดสอบ'}
					</button>
					<a href={p.url} target="_blank"
						class="px-3 py-1.5 rounded-lg text-xs font-semibold border"
						style="border-color: var(--border); color: var(--accent); background: var(--bg);">
						สมัคร →
					</a>
				</div>
			</div>

			<!-- Body -->
			<div class="px-4 py-3">
				<div class="flex items-center gap-3 mb-2">
					<span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--bg3); color: var(--text2);">{p.tier}</span>
					<span class="text-xs" style="color: var(--text3);">{p.desc}</span>
				</div>

				<input type="text" placeholder={p.hint}
					value={keys[p.env] || ''}
					oninput={(e) => onInput(p.env, (e.target as HTMLInputElement).value)}
					class="w-full px-3 py-2.5 rounded-lg border font-mono text-sm"
					style="background: var(--bg); border-color: var(--border); color: var(--text);">

				<!-- Test Result -->
				{#if r}
					<div class="mt-3 px-3 py-2 rounded-lg text-sm"
						style="background: {isOk ? 'rgba(63,185,80,0.1)' : isLimit ? 'rgba(210,153,34,0.1)' : isTesting ? 'rgba(88,166,255,0.1)' : 'rgba(248,81,73,0.1)'};">
						{#if isTesting}
							<div class="flex items-center gap-2" style="color: var(--accent);">
								<span class="animate-spin">⏳</span>
								<span>กำลังทดสอบ {p.name}...</span>
							</div>
						{:else if isOk}
							<div class="flex items-center justify-between">
								<span style="color: var(--green);" class="font-bold">✅ ผ่าน! ใช้ได้จริง</span>
								<span class="font-mono text-xs px-2 py-0.5 rounded" style="background: rgba(63,185,80,0.2); color: var(--green);">
									{r.latency_ms || '?'}ms
								</span>
							</div>
							{#if r.message}
								<div class="text-xs mt-1" style="color: var(--text2);">{r.message}</div>
							{/if}
						{:else if isLimit}
							<div style="color: var(--yellow);" class="font-bold">⚠️ Key ใช้ได้ แต่ถึง rate limit</div>
							<div class="text-xs mt-1" style="color: var(--text2);">รอสักครู่แล้วลองใหม่ หรือใช้ provider อื่นก่อน</div>
						{:else}
							<div style="color: var(--red);" class="font-bold">❌ ไม่ผ่าน</div>
							<div class="text-xs mt-1" style="color: var(--text2);">{r.message || 'Key ไม่ถูกต้องหรือหมดอายุ'}</div>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	{/each}
</div>
