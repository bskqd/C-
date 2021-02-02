<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="changeFullName"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    type="sailorFullNameChanges"
    link="passports-changes-info">
    <SailorFullNameChangesAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorFullNameChanges.js" />
