<template>
    <div id="app">
        <Header />
    </div>
</template>

<script>
import Header from "./components/Header"

export default {
    components: {
        Header
    }
}
</script>

<style>
body, html {
    background-color: #F8F8F8;
    margin: 0;
    padding: 0;
    width: 100%;
    height: 51564px;
}

#app {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 14px;
}

.container /*TODO: Make responsive*/ {
    width: 800px;
    margin: 0 auto;
}
</style>
