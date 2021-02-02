<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addSailorPassport"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    type="sailorPassport"
    link="passports-sailors-info">
    <SailorPassportAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorPassport.js"/>
