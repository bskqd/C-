<template>
  <div>
    <b-card class="vx-card p-2" no-body>
      <StatementsSearch
        :statementETI="true"
        :getReport="sailorETIStatementsSearch"
        report="statementETI"
        ref="search"
      />
    </b-card>
    <b-card class="vx-card p-2" no-body>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :getDocuments="getStatementsETIList"
        link="certification-statements-info"
        type="statementETI"/>
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getStatementsETIList" />
    </b-card>
  </div>
</template>

<script src="./StatementETI.js" />
