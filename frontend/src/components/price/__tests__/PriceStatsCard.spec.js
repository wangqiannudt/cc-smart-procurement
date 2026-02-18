import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'

import PriceStatsCard from '../PriceStatsCard.vue'

describe('PriceStatsCard', () => {
  it('renders min/max/avg labels and values', () => {
    const wrapper = mount(PriceStatsCard, {
      props: {
        priceRange: { min: 1000, max: 3000, avg: 2000 },
        formatPrice: (v) => `¥${v}`
      },
      global: {
        stubs: {
          elIcon: true,
          DataBoard: true
        }
      }
    })

    expect(wrapper.text()).toContain('最低价')
    expect(wrapper.text()).toContain('最高价')
    expect(wrapper.text()).toContain('平均价')
    expect(wrapper.text()).toContain('¥1000')
    expect(wrapper.text()).toContain('¥3000')
    expect(wrapper.text()).toContain('¥2000')
  })
})
