<template>
  <Table
    :viewNewDoc="viewNewDoc"
    labelKeyAdd="addStudentCard"
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="education-student-info"
    type="student">
    <SailorStudentAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./SailorStudent.js"/>
