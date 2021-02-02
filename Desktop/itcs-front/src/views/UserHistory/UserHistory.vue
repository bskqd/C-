<template>
  <div>
    <b-card class="vx-card p-2" no-body>
      <UserHistorySearch
        :userHistory="true"
        :getReport="userHistorySearch"
        report="userHistory"
        ref="search"
      />
    </b-card>
    <b-card class="vx-card" no-body>
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :getDocuments="getUserHistory"
        componentInfo="UserHistoryInfo"
        type="userHistory"/>
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getUserHistory" />
    </b-card>
  </div>
</template>

<script src="./UserHistory.js"/>
