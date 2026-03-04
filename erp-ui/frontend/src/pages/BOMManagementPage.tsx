/**
 * BOM Management Hub Page
 * Landing page with cards linking to BOM Produksi and BOM Purchasing.
 */

import React from 'react'
import { Factory, ShoppingCart } from 'lucide-react'
import { NavigationCard } from '@/components/ui/NavigationCard'

//  Hub Page 

const BOMManagementPage: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Factory className="w-7 h-7 text-blue-600" />
          BOM Management
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Bill of Materials  kelola BOM Produksi dan BOM Purchasing
        </p>
      </div>

      {/* Navigation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl">
        <NavigationCard
          title="BOM Produksi"
          description="Bill of Materials untuk proses produksi. Kelola komponen, qty, dan wastage untuk kategori Production."
          icon={Factory}
          link="/admin/bom-production"
          color="blue"
          badge="Production"
        />
        <NavigationCard
          title="BOM Purchasing"
          description="Bill of Materials untuk proses pembelian. Kelola komponen dan material untuk kategori Purchase."
          icon={ShoppingCart}
          link="/admin/bom-purchase"
          color="purple"
          badge="Purchasing"
        />
      </div>
    </div>
  )
}

export default BOMManagementPage
