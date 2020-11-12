def f1(sand, clay):
    watsat = 0.489 - 0.00126*sand
    bsw    = 2.91 + 0.159*clay
    sucsat = 10. * ( 10.**(1.88-0.0131*sand) )            
    xksat  = 0.0070556 *( 10.**(-0.884+0.0153*sand) ) 

    return watsat, bsw, sucsat, xksat



sand = 40
clay =20

om_frac =0.1
om_watsat         = 0.83

watsat, bsw, sucsat, xksat= f1(sand, clay)
watsat_col   = (1. - om_frac) * watsat + om_watsat * om_frac

print(watsat_col)



