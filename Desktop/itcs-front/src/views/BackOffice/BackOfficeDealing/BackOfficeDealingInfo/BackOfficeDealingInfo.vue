<template>
  <b-card header-tag="header">
    <b-table
      :items="sailorDocument.ntz_ratio"
      :fields="fields"
      striped
      hover
    >
      <template #cell(ntz)="row">
        {{ row.item.ntz.name_ukr }}
      </template>

      <template #cell(ratio)="row">
        {{ (row.item.ratio)*100 }} %
      </template>
    </b-table>
  </b-card>
</template>

<script src="./BackOfficeDealingInfo.js"/>
