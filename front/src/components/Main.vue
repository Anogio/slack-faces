<template>
  <div class="hello">
    <h1>Facedle</h1>
    <table id="puzzle" :style="{width: '90%', margin: '0 auto'}">
      <tr>
      <td v-for="(p, index) in puzzle" :key="index" :style="{display: 'inline-block'  }">
        <img :src="p.picture" :style="{padding: '5px'}"/>
          <n-select v-model="p.guess" class="name-select"
                placeholder="Please select a name" :options="options"/>
        
      </td>
      </tr>
    </table>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  data: () => {
    return {
      puzzle: [],
      options: [],
    }
  },
  async created() {
    const response = await fetch("http://127.0.0.1:5000/puzzle")
    const payload = await response.json()
    console.log(payload)
    this.puzzle = payload.puzzle.map(el => ({picture: el.picture, trueName: el.name, guess: null}))
    this.options = payload.all_names.map(el => ({label: el, value: el}))

    this.guess = [] * this.puzzle.length
    console.log(this.puzzle)
    console.log(this.allNames)
    console.log(this.guess)
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
a {
  color: #42b983;
}
</style>
