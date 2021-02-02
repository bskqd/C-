<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="addNewRecordBook"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    type="serviceRecordBook"
    link="experience-records-info"
    componentAddRecord="SailorRecordBookLineAdd">
    <SailorRecordBookAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorRecordBook.js"/>
