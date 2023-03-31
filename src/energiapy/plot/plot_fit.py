

def distribution(fit_summary: pandas.DataFrame, fit_type: 'str', fig_size: tuple = (16, 6), font_size: int = 16, color: str = 'blue', usetex: bool = False):

    x = numpy.linspace (0, 1, 200) 


    if fit_type == 'norm':
        y = scipy.stats.norm.pdf(x, loc= fit_summary['params'][fitype][0], scale= fit_summary['params'][fitype][1])
        
    if fit_type == 'expon':
        y = scipy.stats.expon.pdf(x, loc= fit_summary['params'][fitype][0], scale= fit_summary['params'][fitype][1])

    if fit_type == 'uniform':
        y = scipy.stats.uniform.pdf(x, loc= fit_summary['params'][fitype][0], scale= fit_summary['params'][fitype][1])

    if fit_type == 'pareto':
        y = scipy.stats.pareto.pdf(x, b = fit_summary['params'][fitype][0], loc= fit_summary['params'][fitype][1], scale= fit_summary['params'][fitype][2])

    if fit_type == 'dweibull':
        y = scipy.stats.dweibull.pdf(x, c = fit_summary['params'][fitype][0], loc= fit_summary['params'][fitype][1], scale= fit_summary['params'][fitype][2])

    if fit_type == 'genextreme':
        y = scipy.stats.genextreme.pdf(x, c = fit_summary['params'][fitype][0], loc= fit_summary['params'][fitype][1], scale= fit_summary['params'][fitype][2])

    if fit_type == 'loggamma':
        y = scipy.stats.loggamma.pdf(x, c = fit_summary['params'][fitype][0], loc= fit_summary['params'][fitype][1], scale= fit_summary['params'][fitype][2])

    if fit_type == 'lognorm':
        y = scipy.stats.lognorm.pdf(x, s= fit_summary['params'][fitype][0], loc= fit_summary['params'][fitype][1], scale= fit_summary['params'][fitype][2])

    if fit_type == 'gamma':
        y = scipy.stats.gamma.pdf(x, a= fit_summary['params'][fitype][0], loc= fit_summary['params'][fitype][1], scale= fit_summary['params'][fitype][2])

    if fit_type == 'beta':
        y = scipy.stats.beta.pdf(x, a= fit_summary['params'][fitype][0], b = fit_summary['params'][fitype][1], loc= fit_summary['params'][fitype][2], scale= fit_summary['params'][fitype][3])

    if fit_type == 't':
        y = scipy.stats.t.pdf(x, df= fit_summary['params'][fitype][0], loc= fit_summary['params'][fitype][1], scale= fit_summary['params'][fitype][2])

    rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size': font_size})


    ax[1].plot(x, y)
    ax[1].set_title(f"{fit['summary'].iloc[0]['name']} with loc = {round(fit['model']['params'][0], 2)}, scale = {round(fit['model']['params'][1], 2)}")
    plt.grid(alpha = 0.4)
    plt.rcdefaults()
    
    
    # fig, ax = plt.subplots(1,2, figsize = fig_size)
    # ax[0].hist(data, edgecolor = 'black', color = color)
    # ax[0].set_xlim([0,1])
    # ax[0].set_title('Histogram')