<template>
  <div>
    <b-card class="vx-card p-2" no-body>
      <StatementsSearch
        :statementAdvanceTraining="true"
        :getReport="advanceTrainingSearch"
        report="statementAdvanceTraining"
        ref="search"
      />
    </b-card>
    <b-card class="vx-card p-2" no-body>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :getDocuments="getAdvanceTrainingStatements"
        link="education-statements-info"
        type="statementAdvanceTraining"/>
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getAdvanceTrainingStatements" />
    </b-card>
  </div>
</template>

<script src="./StatementAdvanceTraining.js" />
