<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="newQualificationStatement"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="qualification-statements-info"
    type="qualificationStatement">

    <SailorQualificationStatementAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorQualificationStatement.js"/>
