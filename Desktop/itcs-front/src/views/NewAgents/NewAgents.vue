<template>
  <div class="vx-card sailorProfilePage">
    <Table
      :items="items"
      :fields="fields"
      :sortBy="sortBy"
      :sortDesc="sortDesc"
      type="newAgents"
      link="agent-statement-info"
    />
  </div>
</template>

<script src="./NewAgents.js" />
