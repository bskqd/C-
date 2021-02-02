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
      v-for="sailor of sailors"
      class="mt-2"
    >
      <a
        :href="`/sailor/${sailor.id}/passports/sailors`"
        class="mb-4"
      >
        <div class="vx-card seafarerItem mb-6 p-2">
            <div class="img-container w-25">
                <img
                  :src="sailor.photo"
                  alt="seafarer-photo"
                  width="125px"
                />
              </div>
            <div class="seafarerInfo vx-col flex-1">
              <div class="vx-row mb-1 pl-3 seafarerInfo-name">
                {{ sailor.FIO_sailor.fio_ukr }}
              </div>
              <div class="vx-row">
                <div class="seafarerInfo-item">
                  <label>
                    {{ $t('dateBorn') }}:
                  </label>
                  <div>
                    {{ getDateFormat(sailor.date_birth) }}
                  </div>
                </div>
                <div class="seafarerInfo-item">
                  <label>
                    {{ $t('serialAndNum') }}:
                  </label>
                  <div>
                    {{ sailor.passport }}
                  </div>
                </div>
                <div class="seafarerInfo-item">
                  <label>
                    {{ $t('taxNumber') }}:
                  </label>
                  <div>
                    {{ sailor.tax_number }}
                  </div>
                </div>
                <div class="seafarerInfo-item">
                  <label>
                    {{ $t('sex') }}:
                  </label>
                  <div>
                    {{ sailor.sex[labelName] }}
                  </div>
                </div>
              </div>
            </div>
        </div>
      </a>
    </div>
  </b-overlay>
</template>

<script src="./MainSailorHistory.js"/>
