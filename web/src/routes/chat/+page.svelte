<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { getModels } from '$lib/api';

	type Msg = { role: 'user' | 'assistant' | 'system'; content: string; provider?: string; latency?: number; model?: string; reason?: string; time?: string; };

	let messages = $state<Msg[]>([]);
	let input = $state('');
	let loading = $state(false);
	let models = $state<any[]>([]);
	let selectedModel = $state('auto');
	let sessionId = $state('chat-' + Date.now().toString(36));
	let chatEl: HTMLDivElement;

	onMount(async () => {
		const m = await getModels();
		if (m?.data) models = m.data;
	});

	async function scrollBottom() {
		await tick();
		if (chatEl) chatEl.scrollTop = chatEl.scrollHeight;
	}

	async function send() {
		const text = input.trim();
		if (!text || loading) return;

		const userMsg: Msg = { role: 'user', content: text, time: new Date().toLocaleTimeString('th-TH', { hour12: false, fractionalSecondDigits: 3 }) };
		messages = [...messages, userMsg];
		input = '';
		loading = true;
		scrollBottom();

		try {
			const apiMessages = messages.filter(m => m.role !== 'system').map(m => ({ role: m.role, content: m.content }));
			const start = performance.now();
			const r = await fetch('/v1/chat/completions', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json', 'X-Session-ID': sessionId },
				body: JSON.stringify({ model: selectedModel, messages: apiMessages, max_tokens: 2000 })
			});
			const d = await r.json();
			const elapsed = Math.round(performance.now() - start);
			const p = d._proxy || {};
			const content = d.choices?.[0]?.message?.content || d.error?.message || 'ไม่ได้รับคำตอบ';

			const aiMsg: Msg = {
				role: 'assistant',
				content,
				provider: p.provider,
				latency: p.latency_ms || elapsed,
				model: p.model,
				reason: p.reason,
				time: new Date().toLocaleTimeString('th-TH', { hour12: false, fractionalSecondDigits: 3 }),
			};
			messages = [...messages, aiMsg];
		} catch (e: any) {
			messages = [...messages, { role: 'assistant', content: `❌ Error: ${e.message}`, time: new Date().toLocaleTimeString('th-TH') }];
		}
		loading = false;
		scrollBottom();
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
	}

	function clearChat() {
		messages = [];
		sessionId = 'chat-' + Date.now().toString(36);
	}
</script>

<div class="flex flex-col" style="height: calc(100vh - 120px);">
	<!-- Header -->
	<div class="flex items-center justify-between px-4 py-3 border-b" style="border-color: var(--border);">
		<div class="flex items-center gap-3">
			<h2 class="text-lg font-bold">💬 Chat</h2>
			<select bind:value={selectedModel}
				class="px-3 py-1.5 rounded-lg text-sm border font-mono"
				style="background: var(--bg); border-color: var(--border); color: var(--text);">
				{#each models as m}
					<option value={m.id}>{m.id} ({m.owned_by})</option>
				{/each}
			</select>
		</div>
		<div class="flex items-center gap-2">
			<span class="text-xs px-2 py-1 rounded" style="background: var(--bg3); color: var(--text2);">
				Session: {sessionId.slice(0, 12)}
			</span>
			<button onclick={clearChat}
				class="px-3 py-1.5 rounded-lg text-xs font-semibold cursor-pointer border"
				style="border-color: var(--red); color: var(--red); background: var(--bg);">
				🗑️ ล้าง
			</button>
		</div>
	</div>

	<!-- Messages -->
	<div bind:this={chatEl} class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
		{#if messages.length === 0}
			<div class="flex items-center justify-center h-full">
				<div class="text-center">
					<div class="text-6xl mb-4">🤖</div>
					<h3 class="text-xl font-bold mb-2">FindFreeAI Chat</h3>
					<p class="text-sm" style="color: var(--text2);">พิมพ์ข้อความด้านล่าง — AI จะตอบผ่าน Proxy ฟรีอัตโนมัติ</p>
					<p class="text-xs mt-2" style="color: var(--text3);">Model: {selectedModel} | RAG Memory จำบทสนทนาให้</p>
				</div>
			</div>
		{/if}

		{#each messages as msg, i}
			{#if msg.role === 'user'}
				<!-- User -->
				<div class="flex justify-end">
					<div class="max-w-2xl">
						<div class="px-4 py-3 rounded-2xl rounded-br-sm" style="background: var(--accent); color: white;">
							<p class="whitespace-pre-wrap">{msg.content}</p>
						</div>
						<div class="text-right text-xs mt-1" style="color: var(--text3);">{msg.time || ''}</div>
					</div>
				</div>
			{:else}
				<!-- AI -->
				<div class="flex justify-start">
					<div class="max-w-2xl w-full">
						<div class="px-4 py-3 rounded-2xl rounded-bl-sm border" style="background: var(--bg2); border-color: var(--border);">
							<p class="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
						</div>
						<!-- Meta -->
						<div class="flex flex-wrap items-center gap-2 mt-1.5">
							{#if msg.provider}
								<span class="text-xs px-2 py-0.5 rounded-full font-semibold" style="background: rgba(63,185,80,0.15); color: var(--green);">
									{msg.provider}
								</span>
							{/if}
							{#if msg.latency}
								<span class="text-xs font-mono px-2 py-0.5 rounded-full" style="background: var(--bg3); color: var(--accent);">
									{msg.latency}ms
								</span>
							{/if}
							{#if msg.model}
								<span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--bg3); color: var(--text3);">
									{msg.model}
								</span>
							{/if}
							{#if msg.reason}
								<span class="text-xs" style="color: var(--text3);">
									{msg.reason}
								</span>
							{/if}
							{#if msg.time}
								<span class="text-xs" style="color: var(--text3);">{msg.time}</span>
							{/if}
						</div>
					</div>
				</div>
			{/if}
		{/each}

		{#if loading}
			<div class="flex justify-start">
				<div class="px-4 py-3 rounded-2xl rounded-bl-sm border" style="background: var(--bg2); border-color: var(--border);">
					<div class="flex items-center gap-2" style="color: var(--text2);">
						<span class="animate-bounce">●</span>
						<span class="animate-bounce" style="animation-delay: 0.1s;">●</span>
						<span class="animate-bounce" style="animation-delay: 0.2s;">●</span>
						<span class="ml-2 text-sm">กำลังคิด...</span>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- Input -->
	<div class="px-4 py-3 border-t" style="border-color: var(--border); background: var(--bg2);">
		<div class="flex gap-3 max-w-4xl mx-auto">
			<textarea
				bind:value={input}
				onkeydown={onKeydown}
				placeholder="พิมพ์ข้อความ... (Enter ส่ง, Shift+Enter ขึ้นบรรทัดใหม่)"
				rows="1"
				class="flex-1 px-4 py-3 rounded-xl border text-sm resize-none"
				style="background: var(--bg); border-color: var(--border); color: var(--text); min-height: 48px; max-height: 150px;"
			></textarea>
			<button onclick={send} disabled={loading || !input.trim()}
				class="px-6 py-3 rounded-xl font-bold text-white cursor-pointer disabled:opacity-40 text-sm"
				style="background: var(--accent);">
				{loading ? '⏳' : '📤 ส่ง'}
			</button>
		</div>
	</div>
</div>
