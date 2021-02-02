<template>
  <div class="col-12">
     <b-col lg="12" class="p-0 mb-2">
       <b-form-group
         label-align-sm="left"
         label-size="sm"
         label-for="Пошук"
         class="mb-0"
       >
         <b-input-group size="sm w-full">
           <b-icon icon="search" class="inline-block search-icon--seafarer ml-2" />
           <input
            v-model="search"
            @input="startSearch"
            :placeholder="$t('goSearch')"
            class="input-rounded-full w-full"
          />
         </b-input-group>
       </b-form-group>
       <div
        v-if="setSearch"
        class="card p-2 mt-2"
       >
         <div class="card-content">
           <div class="card-body search-box">
             <h4 v-if="emptySearchResult">
               {{ $t('emptySearchResult') }}
             </h4>
             <div
               :key="sailor.id"
               v-for="sailor of sailors"
             >
              <a :href="`/sailor/${sailor.id}/passports/sailors`">
                 <div class="flex-row-sb">
                   <div>{{ sailor.id }}</div>
                   <div>{{ sailor.last_name_ukr }} {{ sailor.first_name_ukr }} {{ sailor.middle_name_ukr }}</div>
                   <div>{{ sailor.date_birth.replace(/-/g, '.') }}</div>
                 </div>
               </a>
             </div>
           </div>
         </div>
       </div>
     </b-col>
  </div>
</template>

<script src="./Search.js"></script>

<style >
  a {
    color: #75869b !important;
  }
</style>
