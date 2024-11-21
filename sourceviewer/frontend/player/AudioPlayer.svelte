<script lang="ts">
	import { onMount } from "svelte";
	import { Music } from "@gradio/icons";
	import { format_time, type I18nFormatter } from "@gradio/utils";
	import WaveSurfer from "wavesurfer.js";
	import RegionsPlugin, {type Region} from "wavesurfer.js/dist/plugins/regions";
	import { skip_audio, process_audio } from "../shared/utils";
	import WaveformControls from "../shared/WaveformControls.svelte";
	import { Empty } from "@gradio/atoms";
	import { resolve_wasm_src } from "@gradio/wasm/svelte";
	import type { FileData } from "@gradio/client";
	import type { WaveformOptions, Segment } from "../shared/types";
	import { createEventDispatcher } from "svelte";

	export let value: null | {"segments": Segment[], "sources_file": FileData}= null;
	$: url = value?.sources_file.url;
	export let label: string;
	export let root: string;
	export let i18n: I18nFormatter;
	export let dispatch_blob: (
		blobs: Uint8Array[] | Blob[],
		event: "stream" | "change" | "stop_recording"
	) => Promise<void> = () => Promise.resolve();
	export let interactive = false;
	export let editable = true;
	export let waveform_settings: Record<string, any>;
	export let waveform_options: WaveformOptions;
	export let mode = "";
	export let handle_reset_value: () => void = () => {};

	let container: HTMLDivElement;
	let waveform: WaveSurfer | undefined;
	let wsRegion: RegionsPlugin | undefined;
	let playing = false;

	let timeRef: HTMLTimeElement;
	let durationRef: HTMLTimeElement;
	let audio_duration: number;

	let colors: string[] = ["red", "green", "blue", "yellow", "magenta", "cyan"];

	let trimDuration = 0;

	let show_volume_slider = false;

	const dispatch = createEventDispatcher<{
		stop: undefined;
		play: undefined;
		pause: undefined;
		edit: undefined;
		end: undefined;
	}>();

	const create_waveform = (): void => {
		waveform = WaveSurfer.create({
			container: container,
			...waveform_settings
		});
		waveform.load(root + `/file=${value.sources_file.path}`)
	};

	$: if (container !== undefined) {
		if (waveform !== undefined) waveform.destroy();
		container.innerHTML = "";
		create_waveform();
		playing = false;
	}

	$: waveform?.on("decode", (duration: any) => {
		audio_duration = duration;
		durationRef && (durationRef.textContent = format_time(duration));

		if(!wsRegion){
			wsRegion = waveform.registerPlugin(RegionsPlugin.create())
			value.segments.forEach(segment => {
				const region = wsRegion.addRegion({
					start: segment.start,
					end: segment.end,
					channelIdx: segment.channel,
					drag: false,
					resize: false,
					color: colors[segment.channel % colors.length],
				});
				console.log(region.color)
				const regionHeight = 100 / waveform.getDecodedData().numberOfChannels;
				region.element.style.cssText += `height: ${regionHeight}% !important;`
			});
		}
	});

	$: waveform?.on(
		"timeupdate",
		(currentTime: any) =>
			timeRef && (timeRef.textContent = format_time(currentTime))
	);

	$: waveform?.on("ready", () => {
		if (!waveform_settings.autoplay) {
			waveform?.stop();
		} else {
			waveform?.play();
		}
	});

	$: waveform?.on("finish", () => {
		playing = false;
		dispatch("stop");
	});
	$: waveform?.on("pause", () => {
		playing = false;
		dispatch("pause");
	});
	$: waveform?.on("play", () => {
		playing = true;
		dispatch("play");
	});

	const handle_trim_audio = async (
		start: number,
		end: number
	): Promise<void> => {
		mode = "";
		const decodedData = waveform?.getDecodedData();
		if (decodedData)
			await process_audio(
				decodedData,
				start,
				end,
				waveform_settings.sampleRate
			).then(async (trimmedBlob: Uint8Array) => {
				await dispatch_blob([trimmedBlob], "change");
				waveform?.destroy();
				container.innerHTML = "";
			});
		dispatch("edit");
	};

	async function load_audio(data: string): Promise<void> {
		await resolve_wasm_src(data).then((resolved_src) => {
			if (!resolved_src || value?.sources_file.is_stream) return;
			return waveform?.load(resolved_src);
		});
	}

	$: url && load_audio(url);

	onMount(() => {
		window.addEventListener("keydown", (e) => {
			if (!waveform || show_volume_slider) return;
			if (e.key === "ArrowRight" && mode !== "edit") {
				skip_audio(waveform, 0.1);
			} else if (e.key === "ArrowLeft" && mode !== "edit") {
				skip_audio(waveform, -0.1);
			}
		});
	});
</script>

{#if value === null}
	<Empty size="small">
		<Music />
	</Empty>
{:else if value.sources_file.is_stream}
	<audio
		class="standard-player"
		src={value.sources_file.url}
		controls
		autoplay={waveform_settings.autoplay}
	/>
{:else}
	<div
		class="component-wrapper"
		data-testid={label ? "waveform-" + label : "unlabelled-audio"}
	>
		<div class="waveform-container">
			<div id="waveform" bind:this={container} />
		</div>

		<div class="timestamps">
			<time bind:this={timeRef} id="time">0:00</time>
			<div>
				{#if mode === "edit" && trimDuration > 0}
					<time id="trim-duration">{format_time(trimDuration)}</time>
				{/if}
				<time bind:this={durationRef} id="duration">0:00</time>
			</div>
		</div>

		{#if waveform}
			<WaveformControls
				{waveform}
				{playing}
				{audio_duration}
				{i18n}
				{interactive}
				bind:mode
				bind:trimDuration
				bind:show_volume_slider
				show_redo={interactive}
				{handle_reset_value}
				{waveform_options}
				{editable}
			/>
		{/if}
	</div>
{/if}

<style>
	.component-wrapper {
		padding: var(--size-3);
		width: 100%;
	}

	:global(::part(wrapper)) {
		margin-bottom: var(--size-2);
	}

	.timestamps {
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: 100%;
		padding: var(--size-1) 0;
	}

	#time {
		color: var(--neutral-400);
	}

	#duration {
		color: var(--neutral-400);
	}

	#trim-duration {
		color: var(--color-accent);
		margin-right: var(--spacing-sm);
	}
	.waveform-container {
		display: flex;
		align-items: center;
		justify-content: center;
		width: var(--size-full);
	}

	#waveform {
		width: 100%;
		height: 100%;
		position: relative;
	}

	.standard-player {
		width: 100%;
		padding: var(--size-2);
	}
</style>
