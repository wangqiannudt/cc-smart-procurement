import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'

import PriceSearchCard from '../PriceSearchCard.vue'

describe('PriceSearchCard', () => {
  it('emits search and reset actions', async () => {
    const wrapper = mount(PriceSearchCard, {
      props: {
        modelValue: {
          category: '',
          keyword: '',
          minPrice: null,
          maxPrice: null
        },
        categories: ['服务器'],
        loading: false
      },
      global: {
        plugins: [ElementPlus],
        stubs: {
          Search: true,
          RefreshRight: true
        }
      }
    })

    const queryButton = wrapper.findAll('button').find(btn => btn.text().includes('查询'))
    const resetButton = wrapper.findAll('button').find(btn => btn.text().includes('重置'))

    expect(queryButton).toBeTruthy()
    expect(resetButton).toBeTruthy()

    await queryButton.trigger('click')
    await resetButton.trigger('click')

    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('reset')).toBeTruthy()
  })
})
