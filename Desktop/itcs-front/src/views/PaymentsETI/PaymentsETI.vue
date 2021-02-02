<template>
  <div>
    <b-card class="vx-card p-2" no-body>
      <StatementsSearch
        :etiPayments="true"
        :getReport="sailorPaymentsETISearch"
        report="etiPayments"
        ref="search"
      />
    </b-card>
    <b-card class="vx-card p-2" no-body>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :getDocuments="getPaymentsETI"
        type="etiPayments"/>
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getPaymentsETI" />
    </b-card>
  </div>
</template>

<script src="./PaymentsETI.js" />
