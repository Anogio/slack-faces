<template>
  <div>
    <loading :active="!loaded && !loadFailed" :is-full-page="false" />
    <h1>Facedle</h1>
    <div v-if="loadFailed">
      <n-alert
        title="Could not load puzzle"
        type="error"
        :style="{ maxWidth: '50%', margin: 'auto' }"
      >
        Check that your VPN is enabled
      </n-alert>
    </div>
    <template v-if="loaded">
      <h3>
        Guess which of your coworkers are on the pictures ! They will get less
        pixelated after each guess.
      </h3>
      <table id="puzzle" :style="{ width: '90%', margin: '0 auto' }">
        <tr>
          <td v-for="(p, index) in puzzle" :key="index">
            <img
              alt="mystery slack profile pic"
              :src="p.pixelatedPictureUrl"
              :style="{ width: '200px', height: '200px' }"
            />
            <div v-for="(g, i) in p.pastGuesses" :key="i">
              <n-tag
                :style="{ margin: '5px' }"
                :type="guessTagType(g.match)"
                :bordered="false"
              >
                {{ g.guess }}
              </n-tag>
              <br />
            </div>
            <div v-if="gameFinished && !gameWon">
              <n-tag :style="{ margin: '5px' }" type="info" :bordered="false">
                {{ p.trueName }}
              </n-tag>
              <br />
            </div>
            <n-select
              v-if="!gameFinished"
              :value="p.guess"
              :disabled="
                p.pastGuesses.length > 0 &&
                p.pastGuesses[p.pastGuesses.length - 1].match === EXACT_MATCH
              "
              @update:value="(value) => (p.guess = value)"
              :style="{ maxWidth: '200px', margin: 'auto' }"
              placeholder="Please select a name"
              :options="options"
              clearable
              filterable
              :filter="nameFilter"
            />
          </td>
        </tr>
      </table>
      <br />
      <div v-if="gameFinished">
        <h3 :style="{ margin: '4px' }">
          {{
            gameWon
              ? "Congratulations ! You won. See you tomorrow :)"
              : "You lost ! Try again tomorrow :)"
          }}
        </h3>
        <n-button type="info" @click="copyShareableSummary" size="large" round>
          <template #icon>
            <n-icon> <clipboard /> </n-icon>
          </template>
          {{ shared ? "Copied !" : "Share the results" }}</n-button
        >
      </div>
      <div v-else>
        <n-statistic
          :value="nTries.toString()"
          :style="{
            display: 'inline-block',
            marginRight: '10px',
          }"
        >
          <template #suffix> / {{ maxTries }} guesses </template>
        </n-statistic>
        <n-button type="info" round :disabled="!canSubmit" @click="handleSubmit"
          >Submit</n-button
        >
      </div>
    </template>
  </div>
</template>

<script>
import { Clipboard } from "@vicons/ionicons5";
import Loading from "vue-loading-overlay";
import "vue-loading-overlay/dist/css/index.css";

const EXACT_MATCH = "exact";
const PARTIAL_MATCH = "partial";
const NO_MATCH = "none";

const SERVER_URL = "http://127.0.0.1:5000";
const APP_URL = "https://www.facedle.anog.fr";

function today() {
  const date = new Date();

  let day = date.getDate();
  let month = date.getMonth() + 1;
  let year = date.getFullYear();
  return `${day}/${month}/${year}`;
}

export default {
  name: "FacedleMain",
  components: { Clipboard, Loading },
  data: () => {
    return {
      // These are constants for the game rules
      maxTries: 5,
      imgResolutions: [8, 15, 25, 50, 198],
      EXACT_MATCH,
      // These help maintain some basic state but are reset on every app load
      dayOnAppLoad: today(),
      shared: false,
      loaded: false,
      loadFailed: false,
      // These are the game state, saved after each guess in localStorage, and loaded if they are from today
      puzzle: [],
      options: [],
    };
  },
  async created() {
    const existingState = this.loadAppState();
    if (existingState) {
      this.puzzle = existingState.puzzle;
      this.options = existingState.options;
    } else {
      const response = await this.fetchWithTimeout(
        `${SERVER_URL}/puzzle`,
        5000
      );
      if (response === undefined) {
        this.loadFailed = true;
        return;
      }
      const payload = await response.json();
      this.puzzle = payload.puzzle.map((el) => ({
        pictureUrl: el.picture,
        pixelatedPictureUrl: this.pixelatedPictureUrl(
          el.picture,
          this.imgResolutions[0]
        ),
        trueName: el.name,
        guess: null,
        pastGuesses: [],
      }));
      this.options = payload.all_names.map((el) => ({ label: el, value: el }));
    }
    this.loaded = true;
  },
  computed: {
    canSubmit() {
      return this.puzzle.every((el) => el.guess !== null);
    },
    nTries() {
      return this.puzzle.length ? this.puzzle[0].pastGuesses.length : 0;
    },
    gameWon() {
      return (
        this.puzzle.length &&
        this.puzzle.every(
          (el) =>
            el.pastGuesses.length &&
            el.pastGuesses[el.pastGuesses.length - 1].match === EXACT_MATCH
        )
      );
    },
    gameFinished() {
      return this.gameWon || this.nTries === this.maxTries;
    },
  },
  methods: {
    pixelatedPictureUrl(baseUrl, targetResolution) {
      return `${SERVER_URL}/pixelated_image?image_url=${encodeURIComponent(
        baseUrl
      )}&target_resolution=${targetResolution}`;
    },
    guessTagType(match) {
      return match === EXACT_MATCH
        ? "success"
        : match === PARTIAL_MATCH
        ? "warning"
        : "error";
    },
    handleSubmit() {
      const namesToGuess = this.puzzle.map((p) => p.trueName);

      let match = null;
      this.puzzle.forEach((p) => {
        match = null;
        if (p.guess === p.trueName) {
          match = EXACT_MATCH;
        } else if (namesToGuess.includes(p.guess)) {
          match = PARTIAL_MATCH;
        } else {
          match = NO_MATCH;
        }
        p.pastGuesses.push({ match: match, guess: p.guess });
        if (match !== EXACT_MATCH) {
          p.guess = null;
        }

        p.pixelatedPictureUrl = this.pixelatedPictureUrl(
          p.pictureUrl,
          this.imgResolutions[
            Math.min(
              match === EXACT_MATCH ? this.maxTries : this.nTries,
              this.maxTries - 1
            )
          ]
        );
        this.storeAppState();
      });
    },
    computeSummary() {
      let summaryString = `Facedle ${this.dayOnAppLoad} - ${
        this.gameWon ? this.nTries : "💀"
      }/${this.maxTries}\n\n`;
      for (let i = 0; i < this.nTries; i++) {
        this.puzzle.forEach((p) => {
          let match = p.pastGuesses[i].match;
          let marker =
            match === EXACT_MATCH
              ? "🟩"
              : match === PARTIAL_MATCH
              ? "🟨"
              : "⬛";
          summaryString = summaryString + marker;
        });
        summaryString = summaryString + (i === this.nTries - 1 ? "" : "\n");
      }
      if (this.gameWon) {
        summaryString = summaryString + "🎉";
      }
      summaryString = summaryString + `\n\n${APP_URL}`;
      return summaryString;
    },
    copyShareableSummary() {
      navigator.clipboard.writeText(this.computeSummary());
      this.shared = true;
    },
    normalizeFilterValue(text) {
      return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
    },
    nameFilter(pattern, option) {
      return this.normalizeFilterValue(option.value).startsWith(
        this.normalizeFilterValue(pattern)
      );
    },
    loadAppState() {
      const state = localStorage.getItem(this.dayOnAppLoad);
      return state ? JSON.parse(state) : null;
    },
    storeAppState() {
      localStorage.setItem(
        this.dayOnAppLoad,
        JSON.stringify({
          puzzle: this.puzzle,
          options: this.options,
        })
      );
    },
    async fetchWithTimeout(url, ms, { ...options } = {}) {
      let timeout;
      let result;
      try {
        const controller = new AbortController();
        const promise = fetch(url, { signal: controller.signal, ...options });
        timeout = setTimeout(() => controller.abort(), ms);
        result = await promise;
      } catch (error) {
        console.error(error);
      } finally {
        if (timeout) {
          clearTimeout(timeout);
        }
      }
      return result;
    },
  },
};
</script>

<style scoped></style>
