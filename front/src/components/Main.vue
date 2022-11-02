<template>
  <div class="hello">
    <h1>Facedle</h1>
    <table id="puzzle" :style="{ width: '90%', margin: '0 auto' }">
      <tr>
        <td v-for="(p, index) in puzzle" :key="index">
          <img :src="p.picture" />
          <div v-for="(g, i) in p.pastGuesses" :key="i">
            <n-tag
              :style="{ margin: '5px' }"
              :type="
                g.match === 'exact'
                  ? 'success'
                  : g.match === 'partial'
                  ? 'warning'
                  : 'error'
              "
              :bordered="false"
            >
              {{ g.guess }}
            </n-tag>
            <br />
          </div>
          <n-select
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
    <div v-if="gameWon || nTries === maxTries">FINISH</div>
    <n-button
      v-else
      type="info"
      round
      :disabled="!canSubmit"
      @click="handleSubmit"
      >Submit</n-button
    >
  </div>
</template>

<script>
export default {
  name: "HelloWorld",
  data: () => {
    return {
      puzzle: [],
      options: [],
      gameWon: false,
      maxTries: 5,
      nTries: 0,
    };
  },
  async created() {
    const response = await fetch("http://127.0.0.1:5000/puzzle");
    const payload = await response.json();
    console.log(payload);
    this.puzzle = payload.puzzle.map((el) => ({
      picture: el.picture,
      trueName: el.name,
      guess: null,
      pastGuesses: [],
    }));
    this.options = payload.all_names.map((el) => ({ label: el, value: el }));
    console.log(this.puzzle);
  },
  computed: {
    canSubmit() {
      return this.puzzle.every((el) => el.guess !== null);
    },
  },
  methods: {
    handleSubmit() {
      var success = true;
      const namesToGuess = this.puzzle.map((p) => p.trueName);
      this.puzzle.forEach((p) => {
        var match = null;
        if (p.guess === p.trueName) {
          match = "exact";
        } else if (namesToGuess.includes(p.guess)) {
          match = "partial";
          success = false;
        } else {
          match = "none";
          success = false;
        }

        p.pastGuesses.push({ match: match, guess: p.guess });
        p.guess = null;
      });
      this.gameWon = success;
      this.nTries += 1;
      console.log(this.puzzle);
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
