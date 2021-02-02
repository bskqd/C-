<template>
  <div>
    <div class="vx-card p-2">
      <StatementsSearch
        :getReport="agentStatementsSearch"
        :agentStatements="true"
        report="agentStatements"
        ref="search"
      />
    </div>
    <div class="vx-card mt-2">
      <Table
        :loader="tableLoader"
        :items="items.results"
        :fields="fields"
        :getDocuments="getAgentApplicationFromSailor"
        type="agentStatements"
        link="agent-statement-from-sailor-info"
      />
      <Paginate
        :current="items.current"
        :next="items.next"
        :prev="items.previous"
        :count="items.count"
        :changePage="getAgentApplicationFromSailor" />
    </div>
  </div>
</template>

<script src="./AgentStatements.js" />
