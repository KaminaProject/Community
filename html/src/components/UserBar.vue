<template lang="html">
    <div class="parent">
        <nav id="user-nav">
            <div class="container">
                <p>Kamina</p>
            </div>
        </nav>
    </div>
</template>

<script>
export default {
    name: "UserBar"
}
</script>

<style lang="css">
#user-nav {
    display: flex;
    height: 40px;
    background-color: rgba(36, 30, 32, 0.9);
    color: white;
    justify-content: center;
    align-content: center;
    flex-direction: column;
}

#user-nav p {
    line-height: 40px;
    font-size: 18px;
    margin: 0;
}

.parent {
    position: fixed;
    top: 0;
    left: 0;
    margin: auto;
    width: 100%;
    z-index: 9999;
}
</style>
