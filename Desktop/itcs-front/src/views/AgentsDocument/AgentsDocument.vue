<template>
  <div class="vx-card p-2">
    <Table
      :loader="tableLoader"
      :items="items"
      :fields="fields"
      :getDocuments="getAgentsDocumentsForVerification"
      type="agentDocuments"
    />
  </div>
</template>

<script src="./AgentsDocument.js"/>
