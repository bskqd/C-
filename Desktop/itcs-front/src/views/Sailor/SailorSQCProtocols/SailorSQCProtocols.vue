<template>
  <Table
    :viewNewDoc="newDoc"
    labelKeyAdd="addProtocolSQC"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    type="sailorSQCProtocols"
    link="sqc-protocols-info">
    <SailorSQCProtocolsAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorSQCProtocols.js" />
