<template lang="html">
    <!-- TODO: use dynamic banner image -->
    <div id="community-banner">
        <img src="../../assets/kernel-panic.jpg" alt="Community banner">
    </div>
</template>

<script>
export default {
    name: "CommunityBanner"
}
</script>

<style lang="css">
    #community-banner {
        height: 300px;
        overflow: hidden;
    }

    #community-banner img {
        max-width: 100%;
    }
</style>
