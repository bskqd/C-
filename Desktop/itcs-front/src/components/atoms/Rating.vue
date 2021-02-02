<template>
  <div>
    <b-button @click="readonly ? viewModal = !viewModal : null" class="w-75 no-style">
      <b-form-rating
        v-if="!viewEditOnly"
        v-model="rating"
        @click="viewModal = !viewModal"
        class="cursor-pointer w-100"
        variant="primary"
        disabled
      />
    </b-button>
    <b-modal
      v-model="viewModal"
      :title="$t('setRating')"
      id="modal-rating"
    >
      <b-form-rating
        v-model="newRating"
        variant="primary"
      />
      <template #modal-footer >
        <b-button
          @click="closeRating"
          class="btn-outline-success col-4"
        >
          {{ $t('close') }}
        </b-button>
        <b-button
          @click="setRating"
          class="btn-success col-8 rating-success"
        >
          {{ $t('rating') }}
        </b-button>
      </template>
    </b-modal>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Rating',
  data () {
    return {
      newRating: this.rating,
      viewModal: this.visible
    }
  },
  props: {
    viewEditOnly: Boolean,
    statementId: Number,
    visible: Boolean,
    readonly: Boolean
  },
  computed: {
    ...mapState({
      id: state => state.sailor.sailorId
    }),
    rating: {
      get () {
        return this.$store.state.sailor.rating === null ? 0 : this.$store.state.sailor.rating
      },
      set () {
        return this.rating
      }
    }
  },
  watch: {
    // Check if user click out of modal zone and modal was closed
    viewModal: function (value) {
      if (!value) this.$store.dispatch('getPositionStatements', this.id)
    }
  },
  methods: {
    setRating () {
      this.$bvModal.hide('modal-rating')
      const body = {
        rating: this.newRating,
        statement: this.statementId
      }
      this.$api.post(`api/v2/sailor/${this.id}/rating/`, body)
        .then(response => {
          if (response.code === 200 || response.code === 201) {
            this.$store.commit('setRating', response.data.rating)
            this.$notification.success(this, this.$i18n.t('ratingSuccess'))
          }
        })
    },

    closeRating () {
      this.$bvModal.hide('modal-rating')
      this.$store.dispatch('getPositionStatements', this.id)
    }
  }
}
</script>

<style scoped>
  .no-style, .no-style:hover, .no-style:active, .no-style:focus {
    background: inherit !important;
    border: none !important;
    color: inherit !important;
  }

  .b-rating-star, .b-rating-icon, .b-rating-icon svg {
    cursor: pointer
  }
</style>
