<template>
  <Table
    :items="items"
    :fields="fields"
    :sortBy="sortBy"
    :sortDesc="sortDesc"
    link="coefficients-backoffice-info"
    type="backOfficeCoefficient">
    <CoefficientAdd slot="AddBlock"/>
  </Table>
</template>

<script src="./BackOfficeCoefficients.js"/>
