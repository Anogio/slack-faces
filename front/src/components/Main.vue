<template>
  <div>
    <loading :active="!loaded" :is-full-page="false" />
    <h1>Facedle</h1>
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
            <div v-if="finished && !gameWon">
              <n-tag :style="{ margin: '5px' }" type="info" :bordered="false">
                {{ p.trueName }}
              </n-tag>
              <br />
            </div>
            <n-select
              v-if="!finished"
              :value="p.guess"
              @update:value="(value) => (p.guess = value)"
              :style="{ maxWidth: '200px', margin: 'auto' }"
              placeholder="Please select a name"
              :options="options"
              filterable
            />
          </td>
        </tr>
      </table>
      <br />
      <div v-if="finished">
        <div v-if="gameWon">Congratulations ! You won. See you tomorrow :)</div>
        <div v-else>You lost ! Try again tomorrow :)</div>
        <br />
        <n-button type="info" @click="copyShare">
          <template #icon>
            <n-icon> <clipboard /> </n-icon>
          </template>
          {{ shared ? "Copied !" : "Share" }}</n-button
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

export default {
  name: "FacedleMain",
  components: { Clipboard, Loading },
  data: () => {
    return {
      maxTries: 5,
      puzzle: [],
      options: [],
      gameWon: false,
      nTries: 0,
      summary: "",
      shared: false,
      loaded: false,
      imgResolutions: [8, 15, 25, 50, 198],
    };
  },
  async created() {
    const response = await fetch(`${SERVER_URL}/puzzle`);
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
    this.loaded = true;
  },
  computed: {
    canSubmit() {
      return this.puzzle.every((el) => el.guess !== null);
    },
    finished() {
      return this.gameWon || this.nTries === this.maxTries;
    },
    today() {
      const date = new Date();

      let day = date.getDate();
      let month = date.getMonth() + 1;
      let year = date.getFullYear();
      return `${day}/${month}/${year}`;
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
      this.nTries += 1;

      let success = true;
      const namesToGuess = this.puzzle.map((p) => p.trueName);

      let match = null;
      this.puzzle.forEach((p) => {
        match = null;
        if (p.guess === p.trueName) {
          match = EXACT_MATCH;
        } else if (namesToGuess.includes(p.guess)) {
          match = PARTIAL_MATCH;
          success = false;
        } else {
          match = NO_MATCH;
          success = false;
        }
        p.pastGuesses.push({ match: match, guess: p.guess });
        p.guess = null;

        p.pixelatedPictureUrl = this.pixelatedPictureUrl(
          p.pictureUrl,
          this.imgResolutions[Math.min(this.nTries, this.maxTries - 1)]
        );
      });
      this.gameWon = success;

      if (this.finished) {
        this.summary = this.computeSummary();
      }
    },
    computeSummary() {
      let summaryString = `Facedle ${this.today} - ${
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
      summaryString = summaryString + "\n\nhttps://www.facedle.anog.fr";
      return summaryString;
    },
    copyShare() {
      navigator.clipboard.writeText(this.summary);
      this.shared = true;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
