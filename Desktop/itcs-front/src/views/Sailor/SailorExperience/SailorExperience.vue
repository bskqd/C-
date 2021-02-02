<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addExperienceDoc"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="experience-reference-info"
    type="experience">
    <SailorExperienceAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorExperience.js"/>
