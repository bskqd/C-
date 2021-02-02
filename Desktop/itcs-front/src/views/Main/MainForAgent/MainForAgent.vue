<template>
  <b-overlay
    :show="cardLoader"
    spinner-variant="primary"
    opacity="0.65"
    blur="2px"
    variant="white"
  >
    <div
      :key="sailor.id"
      v-for="sailor in sailors.results"
      class="mt-2"
    >
      <a
        :href="'/sailor/' + sailor.id"
        class="mb-4"
      >
        <div class="vx-card seafarerItem mb-6 p-2">
          <div class="img-container w-25">
                <img
                  :src="sailor.photo"
                  alt="seafarer-photo"
                  width="125px"
                >
              </div>
          <div class="seafarerInfo vx-col flex-1">
              <div class="vx-row mb-1 pl-1 seafarerInfo-name">
                {{ sailor.full_name[labelLang] }}
              </div>
              <div class="vx-row">
                <div class="seafarerInfo-item">
                  <label>
                    {{ $t('dateBorn') }}:
                  </label>
                  {{ getDateFormat(sailor.date_birth) }}
                </div>
                <div class="seafarerInfo-item">
                  <label>
                    {{ $t('serialAndNum') }}:
                  </label>
                  {{ sailor.passport }}
                </div>
                <div class="seafarerInfo-item">
                  <label>
                    {{ $t('taxNumber') }}:
                  </label>
                  {{ sailor.tax_number }}
                </div>
                <div class="seafarerInfo-item">
                  <label>
                    {{ $t('sex') }}:
                  </label>
                  {{ sailor.sex[labelName] }}
                </div>
              </div>
            </div>
        </div>
      </a>
    </div>
    <Paginate
      :current="sailors.current"
      :next="sailors.next"
      :prev="sailors.previous"
      :count="sailors.count"
      :changePage="getSailor"
      amountLabel="seafarersAmount"
    />
  </b-overlay>
</template>

<script src="./MainForAgent.js" />
