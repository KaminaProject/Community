<template>
    <header>
        <!-- Banner + Navigation bar -->
        <UserBar />
        <CommunityBanner />
    </header>
</template>

<script>
import uuid from "uuid"

import UserBar from "./UserBar"
import CommunityBanner from "./community/Banner"

export default {
    name: "Header",
    components: {
        UserBar, CommunityBanner
    }
}
</script>

<style lang="css">
</style>
