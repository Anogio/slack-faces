<template>
  <FacedleMain />
</template>

<script>
import FacedleMain from "./components/Main.vue";

export default {
  name: "App",
  components: {
    FacedleMain,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 10px;
}
</style>
