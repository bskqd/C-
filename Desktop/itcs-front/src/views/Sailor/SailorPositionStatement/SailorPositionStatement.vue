<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="sailorPositionStatementAdd"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="position-statements-info"
    type="positionStatement">
    <SailorPositionStatementAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorPositionStatement.js"/>
