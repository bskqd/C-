<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="addSailorWish"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    type="sailorSQCWishes"
    link="sqc-wishes-info">
    <SailorSQCWishesAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorSQCWishes.js"/>
