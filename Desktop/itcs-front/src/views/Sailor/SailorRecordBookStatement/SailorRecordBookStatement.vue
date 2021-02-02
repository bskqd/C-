<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addStatementRB"
    :items="items"
    :fields="fields"
    link="experience-statements-info"
    type="recordBookStatement">
    <SailorRecordBookStatementAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorRecordBookStatement.js"/>
